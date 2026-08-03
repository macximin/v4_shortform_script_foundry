"""Read-only migration canary for the current Samdo Restaurant EP001-003 files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.artifact_graph import (  # noqa: E402
    ArtifactGraph,
    ArtifactNode,
    ArtifactNodeKind,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
    canonical_text_sha256,
)


CANDIDATE_ROOT = ROOT / "artifacts" / "candidates" / "afterlife_restaurant"
SOURCE_FILES = (
    "2차 최종_제1화 개점 전 한 그릇.md",
    "사람용_제2화 남는 걸로 주십시오_수정_v0.3.md",
    "사람용_제3화 그대의 몫_수정_v0.2.md",
)
STAGES = (
    (
        "v0.1",
        "_archive/2026-08-03_superseded_revisions/촬영고_제1-3화_내용보존_합본_v0.1.md",
        ArtifactNodeKind.HUMAN_SURFACE,
        "p0_surface_candidate",
    ),
    (
        "v0.2",
        "_archive/2026-08-03_superseded_revisions/촬영고_제1-3화_현장표면_합본_v0.2.md",
        ArtifactNodeKind.HUMAN_SURFACE,
        "p0_surface_candidate",
    ),
    (
        "v0.3",
        "_archive/2026-08-03_superseded_revisions/촬영고_제1-3화_현장표면_카메라추천_합본_v0.3.md",
        ArtifactNodeKind.PRODUCTION_ANNOTATION,
        "p1_annotation_candidate_mixed_legacy_file",
    ),
    (
        "v0.4",
        "_archive/2026-08-03_superseded_revisions/촬영고_제1-3화_현장표면_촬영지시정리_합본_v0.4.md",
        ArtifactNodeKind.PRODUCTION_ANNOTATION,
        "p1_annotation_candidate_mixed_legacy_file",
    ),
    (
        "v0.5",
        "촬영고_제1-3화_현장표면_행동연결정리_합본_v0.5.md",
        ArtifactNodeKind.STORY_CHANGE_REQUEST,
        "story_change_request_required",
    ),
)


def byte_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "byte_sha256": byte_sha256(path),
        "canonical_text_sha256": canonical_text_sha256(text),
        "bytes": path.stat().st_size,
    }


def extract_dialogue(text: str) -> tuple[tuple[str, str], ...]:
    dialogue: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = re.match(r"^\s{4}([^\s].*?)\s{2,}([^\s].*)$", line)
        if match:
            speaker = " ".join(match.group(1).split())
            speaker = re.sub(r"\s*\([^)]*\)$", "", speaker)
            dialogue.append((speaker, match.group(2).strip()))
    return tuple(dialogue)


def source_scene_count(text: str) -> int:
    return len(re.findall(r"^## \d+\. ", text, re.MULTILINE))


def surface_scene_count(text: str) -> int:
    return len(re.findall(r"^\d+\. ", text, re.MULTILINE))


def declared_parent_sha256(text: str) -> str | None:
    match = re.search(
        r"기준 촬영고 SHA-256: `([0-9a-f]{64})`",
        text,
    )
    return match.group(1) if match else None


def declared_source_locks(text: str) -> dict[str, str]:
    matches = re.findall(
        r"- `artifacts/candidates/afterlife_restaurant/([^`]+)`\s+"
        r"- SHA-256: `([0-9a-f]{64})`",
        text,
    )
    return dict(matches)


def marker_counts(text: str) -> dict[str, int]:
    return {
        "camera": len(re.findall(r"^CAMERA \(추천\)", text, re.MULTILINE)),
        "shot": len(re.findall(r"^SHOT \(추천\)", text, re.MULTILINE)),
        "insert": len(re.findall(r"^INSERT \(추천\)", text, re.MULTILINE)),
        "edit": len(re.findall(r"^EDIT \(추천\)", text, re.MULTILINE)),
        "sfx_in_or_out": len(
            re.findall(r"^SFX \(화면 (?:안|밖)\)", text, re.MULTILINE)
        ),
    }


def audit() -> dict[str, Any]:
    source_paths = tuple(CANDIDATE_ROOT / name for name in SOURCE_FILES)
    stage_paths = tuple(CANDIDATE_ROOT / item[1] for item in STAGES)
    missing = [path for path in (*source_paths, *stage_paths) if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing canary files: " + ", ".join(str(path) for path in missing)
        )

    source_snapshots = tuple(snapshot(path) for path in source_paths)
    stage_snapshots = tuple(snapshot(path) for path in stage_paths)
    source_texts = tuple(path.read_text(encoding="utf-8") for path in source_paths)
    stage_texts = tuple(path.read_text(encoding="utf-8") for path in stage_paths)

    locked_dialogue = tuple(
        item for text in source_texts for item in extract_dialogue(text)
    )
    locked_scene_count = sum(source_scene_count(text) for text in source_texts)
    source_locks = declared_source_locks(stage_texts[0])
    source_lock_checks = {
        path.name: source_locks.get(path.name) == byte_sha256(path)
        for path in source_paths
    }

    chain_checks: dict[str, bool] = {}
    stages: list[dict[str, Any]] = []
    for index, ((version, _, _, lane), path, text, snap) in enumerate(
        zip(STAGES, stage_paths, stage_texts, stage_snapshots, strict=True)
    ):
        if index > 0:
            parent_version = STAGES[index - 1][0]
            chain_checks[f"{parent_version}->{version}"] = (
                declared_parent_sha256(text) == stage_snapshots[index - 1]["byte_sha256"]
            )
        stages.append(
            {
                "version": version,
                **snap,
                "lane": lane,
                "dialogue_count": len(extract_dialogue(text)),
                "dialogue_exact": extract_dialogue(text) == locked_dialogue,
                "scene_count": surface_scene_count(text),
                "scene_count_exact": surface_scene_count(text) == locked_scene_count,
                "markers": marker_counts(text),
                "auto_promotable": False,
            }
        )

    source_bundle_sha256 = canonical_sha256(source_snapshots)
    nodes = [
        ArtifactNode(
            "locked_source_bundle",
            ArtifactNodeKind.EPISODE_TEXT,
            source_bundle_sha256,
        )
    ]
    dependency = "locked_source_bundle"
    for (version, _, kind, _), snap in zip(STAGES, stage_snapshots, strict=True):
        nodes.append(
            ArtifactNode(
                version,
                kind,
                snap["byte_sha256"],
                (dependency,),
            )
        )
        dependency = version
    graph = ArtifactGraph(
        graph_id="afterlife_restaurant:ep001-003:legacy-production-canary",
        nodes=tuple(nodes),
    )

    v05_has_declared_story_changes = all(
        fragment in stage_texts[-1]
        for fragment in (
            "휴대전화 화면을 병수 쪽으로 돌려 내민다",
            "휴대전화를 카운터 위에 조심히 내려놓는다",
            "휴대전화를 두 손으로 집어 든다",
        )
    )
    checks = {
        "source_byte_locks": all(source_lock_checks.values()),
        "legacy_parent_hash_chain": all(chain_checks.values()),
        "all_dialogue_exact": all(stage["dialogue_exact"] for stage in stages),
        "all_scene_counts_exact": all(stage["scene_count_exact"] for stage in stages),
        "v0.5_routed_as_story_change": v05_has_declared_story_changes
        and stages[-1]["lane"] == "story_change_request_required",
    }
    return {
        "canary_id": graph.graph_id,
        "mode": "read_only",
        "scope": "afterlife_restaurant_ep001-003",
        "source_bundle_sha256": source_bundle_sha256,
        "sources": source_snapshots,
        "source_lock_checks": source_lock_checks,
        "chain_checks": chain_checks,
        "stages": stages,
        "graph_sha256": graph.content_sha256,
        "graph_order": graph.topological_order(),
        "if_locked_text_changes_invalidate": graph.invalidated_descendants(
            "locked_source_bundle"
        ),
        "checks": checks,
        "passed": all(checks.values()),
        "promotion_allowed": False,
        "external_delivery_allowed": False,
        "note": (
            "v0.3-v0.4 are mixed legacy files and must split surface from "
            "annotations before canonical import; v0.5 requires owner-approved "
            "StoryChangeRequest before any text revision."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"canary: {report['canary_id']}")
        print(f"passed: {report['passed']}")
        print(f"graph: {' -> '.join(report['graph_order'])}")
        print(f"dialogue: {report['stages'][0]['dialogue_count']} exact lines")
        print(f"scenes: {report['stages'][0]['scene_count']} exact headings")
        print("v0.5: story_change_request_required")
        print("promotion_allowed: false")
        print("external_delivery_allowed: false")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
