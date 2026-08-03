"""Deterministic human-readable production surfaces for approved script text."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Protocol

from .canonical import canonical_sha256, canonical_text
from .episode_script_text import (
    EpisodeScriptText,
    ScriptAtom,
    ScriptAtomKind,
)


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ProductionSurfaceStatus(StrEnum):
    CANDIDATE = "candidate_surface"
    EQUIVALENT = "equivalent_surface"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class RenderedAtom:
    atom_id: str
    rendered_text: str

    def __post_init__(self) -> None:
        if not self.atom_id.strip():
            raise ValueError("atom_id must not be empty")
        if not self.rendered_text.strip():
            raise ValueError("rendered_text must not be empty")
        if self.rendered_text != canonical_text(self.rendered_text):
            raise ValueError("rendered_text must use LF line endings")


@dataclass(frozen=True, slots=True)
class HumanProductionSurface:
    surface_id: str
    source_episode_text_sha256: str
    profile_id: str
    status: ProductionSurfaceStatus
    rendered_atoms: tuple[RenderedAtom, ...]

    def __post_init__(self) -> None:
        if not self.surface_id.strip() or not self.profile_id.strip():
            raise ValueError("surface_id and profile_id must not be empty")
        if not _SHA256_RE.fullmatch(self.source_episode_text_sha256):
            raise ValueError(
                "source_episode_text_sha256 must be a lowercase SHA-256"
            )
        if not isinstance(self.status, ProductionSurfaceStatus):
            raise TypeError("status must be a ProductionSurfaceStatus")
        if not self.rendered_atoms:
            raise ValueError("surface requires rendered atoms")
        atom_ids = [atom.atom_id for atom in self.rendered_atoms]
        if len(atom_ids) != len(set(atom_ids)):
            raise ValueError("rendered atom ids must be unique")

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "surface_id": self.surface_id,
                "source_episode_text_sha256": self.source_episode_text_sha256,
                "profile_id": self.profile_id,
                "rendered_atoms": self.rendered_atoms,
            }
        )

    @property
    def rendered_text(self) -> str:
        return "\n\n".join(atom.rendered_text for atom in self.rendered_atoms) + "\n"


class ProductionSurfaceRenderer(Protocol):
    profile_id: str

    def render_atom(self, atom: ScriptAtom) -> str: ...


class SamdoKoreanShootingSurfaceRenderer:
    """Minimal owner-selected Korean shooting-script presentation profile."""

    profile_id = "samdo_korean_shooting_surface@0.1"

    def render_atom(self, atom: ScriptAtom) -> str:
        if atom.kind is ScriptAtomKind.DIALOGUE:
            return f"    {atom.speaker_id}    {atom.text}"
        if atom.kind is ScriptAtomKind.PERFORMANCE_CUE:
            return f"    ({atom.text})"
        return atom.text


def build_production_surface(
    source: EpisodeScriptText,
    *,
    surface_id: str,
    renderer: ProductionSurfaceRenderer,
) -> HumanProductionSurface:
    return HumanProductionSurface(
        surface_id=surface_id,
        source_episode_text_sha256=source.content_sha256,
        profile_id=renderer.profile_id,
        status=ProductionSurfaceStatus.CANDIDATE,
        rendered_atoms=tuple(
            RenderedAtom(atom.atom_id, renderer.render_atom(atom))
            for atom in source.atoms
        ),
    )


@dataclass(frozen=True, slots=True)
class SurfaceFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class SurfaceVerificationReport:
    surface_id: str
    findings: tuple[SurfaceFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class ProductionSurfaceVerifier:
    def verify(
        self,
        surface: HumanProductionSurface,
        source: EpisodeScriptText,
        renderer: ProductionSurfaceRenderer,
    ) -> SurfaceVerificationReport:
        findings: list[SurfaceFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(SurfaceFinding(code, location, message))

        if surface.source_episode_text_sha256 != source.content_sha256:
            hard(
                "SOURCE_TEXT_HASH_MISMATCH",
                "source_episode_text_sha256",
                "surface must bind the exact episode text",
            )
        if surface.profile_id != renderer.profile_id:
            hard(
                "SURFACE_PROFILE_MISMATCH",
                "profile_id",
                "surface profile must match the active renderer",
            )
        expected_ids = tuple(atom.atom_id for atom in source.atoms)
        actual_ids = tuple(atom.atom_id for atom in surface.rendered_atoms)
        if actual_ids != expected_ids:
            hard(
                "ATOM_ORDER_OR_COVERAGE_MISMATCH",
                "rendered_atoms",
                "surface must preserve every source atom in exact order",
            )
        rendered_by_id = {atom.atom_id: atom for atom in surface.rendered_atoms}
        for atom in source.atoms:
            rendered = rendered_by_id.get(atom.atom_id)
            if rendered is None:
                continue
            expected = renderer.render_atom(atom)
            if rendered.rendered_text != expected:
                hard(
                    "RENDERED_ATOM_MISMATCH",
                    atom.atom_id,
                    "surface text must exactly match the deterministic profile",
                )
        if surface.status is ProductionSurfaceStatus.STALE:
            hard("STALE_SURFACE", "status", "stale surfaces cannot pass")
        return SurfaceVerificationReport(surface.surface_id, tuple(findings))
