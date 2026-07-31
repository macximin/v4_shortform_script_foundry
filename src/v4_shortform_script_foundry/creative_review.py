"""Creative quality floor, independent reviews, and pairwise selection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .approval import ApprovalReceipt, HilGate, ReviewDecision
from .arc_contract import ArcContract
from .episode_script import (
    EpisodeScriptCandidate,
    EpisodeScriptVerifier,
)


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ReviewLane(StrEnum):
    BR0 = "br0"
    BR1 = "br1"


class CreativeAxis(StrEnum):
    CAUSAL_COHERENCE = "causal_coherence"
    CHARACTER_INTENTIONALITY = "character_intentionality"
    SCENE_NECESSITY = "scene_necessity"
    VISUAL_EXECUTION = "visual_execution"
    WORK_SPECIFICITY = "work_specificity"
    EMOTIONAL_SPECIFICITY = "emotional_specificity"
    TENSION = "tension"
    REWARD_EXPERIENCE = "reward_experience"
    CLOSURE_OR_CLIFF = "closure_or_cliff"
    DIALOGUE_DISTINCTION = "dialogue_distinction"


COMMON_FLOOR_AXES: tuple[CreativeAxis, ...] = (
    CreativeAxis.CAUSAL_COHERENCE,
    CreativeAxis.CHARACTER_INTENTIONALITY,
    CreativeAxis.SCENE_NECESSITY,
    CreativeAxis.VISUAL_EXECUTION,
    CreativeAxis.WORK_SPECIFICITY,
)


@dataclass(frozen=True, slots=True)
class CreativeScore:
    axis: CreativeAxis
    score: int
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.axis, CreativeAxis):
            raise TypeError("axis must be a CreativeAxis")
        if not 1 <= self.score <= 5:
            raise ValueError("creative score must be between 1 and 5")
        if not self.rationale.strip():
            raise ValueError("creative score rationale must not be empty")


@dataclass(frozen=True, slots=True)
class CreativeReview:
    lane: ReviewLane
    reviewer_id: str
    candidate_content_sha256: str
    rubric_version: str
    scores: tuple[CreativeScore, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.lane, ReviewLane):
            raise TypeError("lane must be a ReviewLane")
        if not self.reviewer_id.strip():
            raise ValueError("reviewer_id must not be empty")
        if not self.rubric_version.strip():
            raise ValueError("rubric_version must not be empty")
        if not _SHA256_RE.fullmatch(self.candidate_content_sha256):
            raise ValueError("candidate_content_sha256 must be a lowercase SHA-256")
        axes = [score.axis for score in self.scores]
        if len(axes) != len(set(axes)):
            raise ValueError("creative review axes must be unique")


@dataclass(frozen=True, slots=True)
class PairwiseComparison:
    reviewer_id: str
    candidate_a_sha256: str
    candidate_b_sha256: str
    preferred_candidate_sha256: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.reviewer_id.strip():
            raise ValueError("reviewer_id must not be empty")
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty")
        for field_name in (
            "candidate_a_sha256",
            "candidate_b_sha256",
            "preferred_candidate_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")
        candidates = {
            self.candidate_a_sha256,
            self.candidate_b_sha256,
        }
        if len(candidates) != 2:
            raise ValueError("pairwise comparison requires different candidates")
        if self.preferred_candidate_sha256 not in candidates:
            raise ValueError(
                "preferred candidate must be one of the compared candidates"
            )


@dataclass(frozen=True, slots=True)
class CreativeFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class CreativeQualityReport:
    candidate_content_sha256: str
    findings: tuple[CreativeFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class CreativeQualityGate:
    def __init__(self, *, minimum_common_score: int = 3) -> None:
        if not 1 <= minimum_common_score <= 5:
            raise ValueError("minimum_common_score must be between 1 and 5")
        self._minimum_common_score = minimum_common_score

    def verify(
        self,
        candidate: EpisodeScriptCandidate,
        reviews: tuple[CreativeReview, ...],
    ) -> CreativeQualityReport:
        findings: list[CreativeFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(CreativeFinding(code, location, message))

        by_lane = {review.lane: review for review in reviews}
        if len(by_lane) != len(reviews):
            hard(
                "DUPLICATE_REVIEW_LANE",
                "reviews",
                "each review lane may appear only once",
            )
        for lane in ReviewLane:
            if lane not in by_lane:
                hard(
                    "MISSING_REVIEW_LANE",
                    "reviews",
                    f"missing independent review lane {lane.value}",
                )
        reviewer_ids = [review.reviewer_id for review in reviews]
        if len(reviewer_ids) != len(set(reviewer_ids)):
            hard(
                "REVIEWERS_NOT_INDEPENDENT",
                "reviews",
                "BR0 and BR1 must use different reviewers",
            )
        if candidate.producer_id in reviewer_ids:
            hard(
                "PRODUCER_REVIEW_CONFLICT",
                "reviews",
                "producer cannot act as BR0 or BR1",
            )

        for review in reviews:
            location = f"reviews.{review.lane.value}"
            if review.candidate_content_sha256 != candidate.content_sha256:
                hard(
                    "CANDIDATE_HASH_MISMATCH",
                    location,
                    "review must bind the exact candidate",
                )
            scores = {score.axis: score.score for score in review.scores}
            for axis in COMMON_FLOOR_AXES:
                if axis not in scores:
                    hard(
                        "MISSING_COMMON_AXIS",
                        location,
                        f"missing common quality axis {axis.value}",
                    )
                elif scores[axis] < self._minimum_common_score:
                    hard(
                        "CREATIVE_FLOOR_NOT_MET",
                        f"{location}.{axis.value}",
                        (
                            f"{axis.value} must score at least "
                            f"{self._minimum_common_score}"
                        ),
                    )
        return CreativeQualityReport(
            candidate_content_sha256=candidate.content_sha256,
            findings=tuple(findings),
        )


@dataclass(frozen=True, slots=True)
class CandidateSetReport:
    candidate_content_sha256s: tuple[str, ...]
    findings: tuple[CreativeFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class CandidateSetVerifier:
    def verify(
        self,
        candidates: tuple[EpisodeScriptCandidate, ...],
    ) -> CandidateSetReport:
        findings: list[CreativeFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(CreativeFinding(code, location, message))

        if not 2 <= len(candidates) <= 4:
            hard(
                "CANDIDATE_COUNT_OUT_OF_RANGE",
                "candidates",
                "candidate set must contain between two and four scripts",
            )
        hashes = tuple(candidate.content_sha256 for candidate in candidates)
        if len(hashes) != len(set(hashes)):
            hard(
                "DUPLICATE_CANDIDATE",
                "candidates",
                "candidate content hashes must be unique",
            )
        work_keys = {
            (
                candidate.work_id,
                candidate.arc_id,
                candidate.episode_id,
            )
            for candidate in candidates
        }
        if len(work_keys) > 1:
            hard(
                "CANDIDATE_SCOPE_MISMATCH",
                "candidates",
                "candidates must target the same work, arc, and episode",
            )
        structure_hashes = {candidate.structure_sha256 for candidate in candidates}
        if len(candidates) >= 2 and len(structure_hashes) < 2:
            hard(
                "CANDIDATES_NOT_STRUCTURALLY_DISTINCT",
                "candidates",
                "candidate set must contain different scene structures",
            )
        return CandidateSetReport(
            candidate_content_sha256s=hashes,
            findings=tuple(findings),
        )


@dataclass(frozen=True, slots=True)
class PromotionReadinessReport:
    candidate_content_sha256: str
    findings: tuple[CreativeFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class PromotionReadinessVerifier:
    def verify(
        self,
        *,
        candidate: EpisodeScriptCandidate,
        arc: ArcContract,
        creative_reviews: tuple[CreativeReview, ...],
        candidates: tuple[EpisodeScriptCandidate, ...],
        pairwise_comparisons: tuple[PairwiseComparison, ...],
        owner_receipt: ApprovalReceipt,
    ) -> PromotionReadinessReport:
        findings: list[CreativeFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(CreativeFinding(code, location, message))

        candidate_set_report = CandidateSetVerifier().verify(candidates)

        if not candidate_set_report.passed:
            hard(
                "CANDIDATE_SET_FAILED",
                "candidate_set_report",
                "candidate cannot be promoted from an invalid candidate set",
            )
        if (
            candidate.content_sha256
            not in candidate_set_report.candidate_content_sha256s
        ):
            hard(
                "CANDIDATE_SET_BINDING_MISMATCH",
                "candidate_set_report",
                "candidate set report must include the selected candidate",
            )

        candidate_hashes = {
            pool_candidate.content_sha256 for pool_candidate in candidates
        }
        if any(
            review.candidate_content_sha256 not in candidate_hashes
            for review in creative_reviews
        ):
            hard(
                "CREATIVE_REVIEW_SET_MISMATCH",
                "creative_reviews",
                "creative reviews must bind candidates in the verified set",
            )

        reviewers_by_lane = {
            lane: {
                review.reviewer_id for review in creative_reviews if review.lane is lane
            }
            for lane in ReviewLane
        }
        if any(len(reviewers) != 1 for reviewers in reviewers_by_lane.values()):
            hard(
                "REVIEWER_PANEL_INCONSISTENT",
                "creative_reviews",
                "one stable reviewer per BR lane must compare the pool",
            )

        for pool_candidate in candidates:
            pool_hard_report = EpisodeScriptVerifier().verify(
                pool_candidate,
                arc,
            )
            if not pool_hard_report.passed:
                hard(
                    "CANDIDATE_POOL_HARD_FAILURE",
                    pool_candidate.content_sha256,
                    "every ranked candidate must pass hard verification",
                )
            pool_reviews = tuple(
                review
                for review in creative_reviews
                if review.candidate_content_sha256 == pool_candidate.content_sha256
            )
            pool_creative_report = CreativeQualityGate().verify(
                pool_candidate,
                pool_reviews,
            )
            if not pool_creative_report.passed:
                hard(
                    "CANDIDATE_POOL_CREATIVE_FLOOR_FAILED",
                    pool_candidate.content_sha256,
                    "every ranked candidate must pass the creative floor",
                )

        if not pairwise_comparisons:
            hard(
                "MISSING_PAIRWISE_COMPARISON",
                "pairwise_comparisons",
                "owner selection requires at least one pairwise comparison",
            )
        else:
            if any(
                comparison.candidate_a_sha256 not in candidate_hashes
                or comparison.candidate_b_sha256 not in candidate_hashes
                for comparison in pairwise_comparisons
            ):
                hard(
                    "PAIRWISE_SET_BINDING_MISMATCH",
                    "pairwise_comparisons",
                    "pairwise comparisons must use the verified candidate set",
                )
            comparison_reviewers = {
                comparison.reviewer_id for comparison in pairwise_comparisons
            }
            required_reviewers = set().union(*reviewers_by_lane.values())
            if not required_reviewers.issubset(comparison_reviewers):
                hard(
                    "PAIRWISE_REVIEWERS_INCOMPLETE",
                    "pairwise_comparisons",
                    "both independent reviewers must compare candidates",
                )
            if not any(
                comparison.preferred_candidate_sha256 == candidate.content_sha256
                for comparison in pairwise_comparisons
            ):
                hard(
                    "CANDIDATE_NOT_PREFERRED",
                    "pairwise_comparisons",
                    "candidate must win at least one bound comparison",
                )
        if owner_receipt.gate_id is not HilGate.HIL3_EPISODE_SCRIPT:
            hard(
                "OWNER_RECEIPT_GATE_MISMATCH",
                "owner_receipt.gate_id",
                "owner receipt must belong to HIL 3",
            )
        if owner_receipt.reviewer_role != "owner":
            hard(
                "OWNER_ROLE_REQUIRED",
                "owner_receipt.reviewer_role",
                "HIL 3 promotion requires the owner role",
            )
        if owner_receipt.decision is not ReviewDecision.APPROVE:
            hard(
                "OWNER_DID_NOT_APPROVE",
                "owner_receipt.decision",
                "owner receipt must explicitly approve",
            )
        if owner_receipt.artifact_content_sha256 != candidate.content_sha256:
            hard(
                "OWNER_RECEIPT_HASH_MISMATCH",
                "owner_receipt.artifact_content_sha256",
                "owner receipt must bind the exact candidate",
            )
        if (
            owner_receipt.work_id != candidate.work_id
            or owner_receipt.artifact_id != candidate.artifact_id
            or owner_receipt.revision != candidate.revision
        ):
            hard(
                "OWNER_RECEIPT_ARTIFACT_MISMATCH",
                "owner_receipt",
                "owner receipt must bind the candidate identity and revision",
            )
        if owner_receipt.parent_content_sha256s != (
            candidate.parent_arc_content_sha256,
        ):
            hard(
                "OWNER_RECEIPT_PARENT_CONTENT_MISMATCH",
                "owner_receipt.parent_content_sha256s",
                "owner receipt must bind the candidate Arc content hash",
            )
        if owner_receipt.parent_approval_receipt_sha256s != (
            candidate.parent_arc_approval_receipt_sha256,
        ):
            hard(
                "OWNER_RECEIPT_PARENT_APPROVAL_MISMATCH",
                "owner_receipt.parent_approval_receipt_sha256s",
                "owner receipt must bind the Arc approval receipt",
            )
        return PromotionReadinessReport(
            candidate_content_sha256=candidate.content_sha256,
            findings=tuple(findings),
        )
