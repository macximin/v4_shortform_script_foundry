"""Ordered HIL 3 screenplay text atoms and stable content identity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256, canonical_text


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


class ScriptAtomKind(StrEnum):
    SCENE_HEADING = "scene_heading"
    ACTION = "action"
    DIALOGUE = "dialogue"
    PERFORMANCE_CUE = "performance_cue"
    SFX = "sfx"
    TRANSITION = "transition"
    SCREEN_TEXT = "screen_text"


class EpisodeScriptTextStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class ScriptAtom:
    atom_id: str
    scene_id: str
    ordinal: int
    kind: ScriptAtomKind
    text: str
    speaker_id: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.atom_id, "atom_id")
        _require_text(self.scene_id, "scene_id")
        _require_text(self.text, "text")
        if self.ordinal < 1:
            raise ValueError("ordinal must be positive")
        if not isinstance(self.kind, ScriptAtomKind):
            raise TypeError("kind must be a ScriptAtomKind")
        if self.text != canonical_text(self.text):
            raise ValueError("atom text must use LF line endings")
        if self.kind is ScriptAtomKind.DIALOGUE:
            if self.speaker_id is None:
                raise ValueError("dialogue atoms require speaker_id")
            _require_text(self.speaker_id, "speaker_id")
        elif self.speaker_id is not None:
            raise ValueError("speaker_id is only valid for dialogue atoms")

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "atom_id": self.atom_id,
                "scene_id": self.scene_id,
                "ordinal": self.ordinal,
                "kind": self.kind,
                "text": self.text,
                "speaker_id": self.speaker_id,
            }
        )


@dataclass(frozen=True, slots=True)
class EpisodeScriptText:
    work_id: str
    episode_id: str
    revision: int
    parent_episode_contract_sha256: str
    status: EpisodeScriptTextStatus
    atoms: tuple[ScriptAtom, ...]

    def __post_init__(self) -> None:
        _require_text(self.work_id, "work_id")
        _require_text(self.episode_id, "episode_id")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        if not _SHA256_RE.fullmatch(self.parent_episode_contract_sha256):
            raise ValueError(
                "parent_episode_contract_sha256 must be a lowercase SHA-256"
            )
        if not isinstance(self.status, EpisodeScriptTextStatus):
            raise TypeError("status must be an EpisodeScriptTextStatus")
        if not self.atoms:
            raise ValueError("episode script text requires at least one atom")

        atom_ids = [atom.atom_id for atom in self.atoms]
        if len(atom_ids) != len(set(atom_ids)):
            raise ValueError("atom ids must be unique")
        ordinals = [atom.ordinal for atom in self.atoms]
        if ordinals != list(range(1, len(self.atoms) + 1)):
            raise ValueError("atom ordinals must be contiguous and ordered")

        seen_scenes: set[str] = set()
        current_scene_id: str | None = None
        for atom in self.atoms:
            if atom.scene_id != current_scene_id:
                if atom.scene_id in seen_scenes:
                    raise ValueError("scene atoms must form one contiguous block")
                seen_scenes.add(atom.scene_id)
                current_scene_id = atom.scene_id
                if atom.kind is not ScriptAtomKind.SCENE_HEADING:
                    raise ValueError("each scene must begin with a scene heading atom")
            elif atom.kind is ScriptAtomKind.SCENE_HEADING:
                raise ValueError("a scene may contain only one scene heading atom")

    @property
    def artifact_id(self) -> str:
        return f"{self.episode_id}:text:r{self.revision}"

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "work_id": self.work_id,
                "episode_id": self.episode_id,
                "revision": self.revision,
                "parent_episode_contract_sha256": (
                    self.parent_episode_contract_sha256
                ),
                "atoms": self.atoms,
            }
        )

    @property
    def scene_ids(self) -> tuple[str, ...]:
        return tuple(
            atom.scene_id
            for atom in self.atoms
            if atom.kind is ScriptAtomKind.SCENE_HEADING
        )

    def atom(self, atom_id: str) -> ScriptAtom:
        for atom in self.atoms:
            if atom.atom_id == atom_id:
                return atom
        raise KeyError(atom_id)
