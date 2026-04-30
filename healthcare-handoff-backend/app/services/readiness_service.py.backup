"""Readiness validation service for handoff acceptance."""

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.handoff import Handoff, HandoffPriorityEnum
from app.models.handoff_item import HandoffItem, ItemTypeEnum, ItemStatusEnum
from app.repositories.handoff_repo import HandoffRepository
from app.repositories.item_repo import HandoffItemRepository
from app.exceptions import HandoffNotReady


class ReadinessService:
    """Service for validating handoff readiness before acceptance."""

    # Vague language patterns to reject
    VAGUE_PHRASES = {
        "check soon",
        "review later",
        "monitor closely",
        "as needed",
        "prn",
        "asap",
        "when possible",
        "follow up soon",
        "check later",
        "see how it goes",
    }

    def __init__(self, db: Session):
        self.db = db
        self.handoff_repo = HandoffRepository(db)
        self.item_repo = HandoffItemRepository(db)

    def validate_handoff(self, handoff: Handoff) -> Dict[str, Any]:
        """
        Validate handoff readiness against 7 rules.
        
        Returns:
            {
                "is_ready": bool,
                "failures": list of failure reasons,
                "warnings": list of warnings (non-blocking)
            }
        """
        
        failures = []
        warnings = []

        # Rule 1: diagnosis_summary provided and not empty
        if not handoff.diagnosis_summary or len(handoff.diagnosis_summary.strip()) == 0:
            failures.append("Diagnosis summary is required")
        elif len(handoff.diagnosis_summary) > 500:
            failures.append("Diagnosis summary must be ≤500 characters")

        # Rule 2: follow_up_deadline is in the future
        if not handoff.follow_up_deadline:
            failures.append("Follow-up deadline is required")
        elif handoff.follow_up_deadline <= datetime.utcnow():
            failures.append("Follow-up deadline must be in the future")

        # Get all items for this handoff
        items = self.item_repo.find_by_handoff(handoff.id)

        # Rule 3: All FOLLOW_UP items must be assigned
        follow_up_items = [i for i in items if i.item_type == ItemTypeEnum.FOLLOW_UP]
        unassigned_follow_ups = [i for i in follow_up_items if not i.assigned_to]
        if unassigned_follow_ups:
            failures.append(f"{len(unassigned_follow_ups)} follow-up items are unassigned")

        # Rule 4: All MEDICATION items must have rationale (description >20 chars)
        med_items = [i for i in items if i.item_type == ItemTypeEnum.MEDICATION]
        for med in med_items:
            if not med.description or len(med.description) < 20:
                failures.append(f"Medication '{med.title}' requires rationale (≥20 characters)")

        # Rule 5: All LAB_TEST items must have due_date
        lab_items = [i for i in items if i.item_type == ItemTypeEnum.LAB_TEST]
        undated_labs = [i for i in lab_items if not i.due_date]
        if undated_labs:
            failures.append(f"{len(undated_labs)} lab test items are missing due dates")

        # Rule 6: CRITICAL priority handoffs must have all items owned
        if handoff.priority == HandoffPriorityEnum.CRITICAL:
            unowned = [i for i in items if not i.assigned_to]
            if unowned:
                failures.append(f"CRITICAL handoff: {len(unowned)} items are unassigned")

        # Rule 7: No vague language in diagnosis summary or item descriptions
        vague_found = self._check_vague_language(handoff, items)
        if vague_found:
            failures.extend(vague_found)

        # Warnings (non-blocking)
        if len(items) == 0:
            warnings.append("Handoff has no items")

        open_items = [i for i in items if i.status == ItemStatusEnum.OPEN]
        if open_items:
            warnings.append(f"{len(open_items)} items are still open")

        return {
            "is_ready": len(failures) == 0,
            "failures": failures,
            "warnings": warnings,
        }

    def _check_vague_language(self, handoff: Handoff, items: List[HandoffItem]) -> List[str]:
        """Check for vague language in diagnosis and items."""
        
        issues = []

        # Check diagnosis summary
        diagnosis_lower = handoff.diagnosis_summary.lower() if handoff.diagnosis_summary else ""
        for phrase in self.VAGUE_PHRASES:
            if phrase in diagnosis_lower:
                issues.append(f"Diagnosis contains vague language: '{phrase}'")

        # Check item descriptions
        for item in items:
            if item.description:
                desc_lower = item.description.lower()
                for phrase in self.VAGUE_PHRASES:
                    if phrase in desc_lower:
                        issues.append(f"Item '{item.title}' contains vague language: '{phrase}'")

        return issues

    def get_readiness_summary(self, handoff: Handoff) -> Dict[str, Any]:
        """Get human-readable readiness check summary."""
        
        result = self.validate_handoff(handoff)
        items = self.item_repo.find_by_handoff(handoff.id)

        return {
            "handoff_id": handoff.id,
            "patient_id": handoff.patient_id,
            "status": handoff.status.value,
            "is_ready": result["is_ready"],
            "total_items": len(items),
            "items_by_status": {
                "open": len([i for i in items if i.status == ItemStatusEnum.OPEN]),
                "in_progress": len([i for i in items if i.status == ItemStatusEnum.IN_PROGRESS]),
                "completed": len([i for i in items if i.status == ItemStatusEnum.COMPLETED]),
            },
            "failures": result["failures"],
            "warnings": result["warnings"],
            "checked_at": datetime.utcnow().isoformat(),
        }

    def assert_ready(self, handoff: Handoff) -> None:
        """Raise exception if handoff is not ready."""
        
        result = self.validate_handoff(handoff)
        if not result["is_ready"]:
            raise HandoffNotReady(result["failures"])