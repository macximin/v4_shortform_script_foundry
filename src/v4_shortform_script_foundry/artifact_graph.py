"""Hash-bound artifact DAG for the conversational production pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ArtifactNodeKind(StrEnum):
    EPISODE_TEXT = "episode_text"
    HUMAN_SURFACE = "human_surface"
    PRODUCTION_ANNOTATION = "production_annotation"
    APPROVAL_RECEIPT = "approval_receipt"
    PRODUCTION_PACKAGE = "production_package"
    STORY_CHANGE_REQUEST = "story_change_request"
    SHOT_PLAN = "shot_plan"
    GENERATED_VIDEO = "generated_video"


@dataclass(frozen=True, slots=True)
class ArtifactNode:
    node_id: str
    kind: ArtifactNodeKind
    content_sha256: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.node_id.strip():
            raise ValueError("node_id must not be empty")
        if not isinstance(self.kind, ArtifactNodeKind):
            raise TypeError("kind must be an ArtifactNodeKind")
        if not _SHA256_RE.fullmatch(self.content_sha256):
            raise ValueError("content_sha256 must be a lowercase SHA-256")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError("dependencies must be unique")
        if self.node_id in self.depends_on:
            raise ValueError("a node cannot depend on itself")


@dataclass(frozen=True, slots=True)
class ArtifactGraph:
    graph_id: str
    nodes: tuple[ArtifactNode, ...]

    def __post_init__(self) -> None:
        if not self.graph_id.strip():
            raise ValueError("graph_id must not be empty")
        if not self.nodes:
            raise ValueError("graph requires at least one node")

        node_ids = tuple(node.node_id for node in self.nodes)
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node ids must be unique")
        known = set(node_ids)
        for node in self.nodes:
            missing = set(node.depends_on) - known
            if missing:
                raise ValueError(
                    f"node {node.node_id} has unknown dependencies: {sorted(missing)}"
                )
        self.topological_order()

    @property
    def content_sha256(self) -> str:
        return canonical_sha256({"graph_id": self.graph_id, "nodes": self.nodes})

    def node(self, node_id: str) -> ArtifactNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(node_id)

    def topological_order(self) -> tuple[str, ...]:
        """Return dependency-first order and reject cycles."""

        ordered: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            if node_id in visiting:
                raise ValueError("artifact graph must be acyclic")
            visiting.add(node_id)
            for dependency in self.node(node_id).depends_on:
                visit(dependency)
            visiting.remove(node_id)
            visited.add(node_id)
            ordered.append(node_id)

        for node in self.nodes:
            visit(node.node_id)
        return tuple(ordered)

    def invalidated_descendants(self, changed_node_id: str) -> tuple[str, ...]:
        """Return every downstream node invalidated by a changed content hash."""

        self.node(changed_node_id)
        invalidated: set[str] = set()
        changed = True
        while changed:
            changed = False
            for node in self.nodes:
                if node.node_id == changed_node_id or node.node_id in invalidated:
                    continue
                if changed_node_id in node.depends_on or any(
                    dependency in invalidated for dependency in node.depends_on
                ):
                    invalidated.add(node.node_id)
                    changed = True
        return tuple(
            node_id
            for node_id in self.topological_order()
            if node_id in invalidated
        )
