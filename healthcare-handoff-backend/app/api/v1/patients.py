"""Patient endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.dependencies import get_current_user, require_role, CurrentUser
from app.schemas.patient import PatientCreate, PatientResponse
from app.models.patient import Patient
from app.repositories.patient_repo import PatientRepository
from app.exceptions import ResourceNotFound, MRNAlreadyExists
from app.services.audit_service import AuditService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: PatientCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("doctor", "admin")),
):
    """Create a new patient (doctor/admin only)."""
    
    repo = PatientRepository(db)
    audit = AuditService(db)
    
    existing = repo.find_by_mrn(request.mrn)
    if existing:
        raise MRNAlreadyExists(request.mrn)
    
    patient = Patient(
        id=str(uuid.uuid4()),
        mrn=request.mrn,
        name=request.name,
        date_of_birth=request.date_of_birth,
        created_by=current_user.user_id,
    )
    
    patient = repo.create(patient)
    
    audit.log_action(
        user_id=current_user.user_id,
        entity_type="PATIENT",
        entity_id=patient.id,
        action="CREATE",
        new_values=patient.to_dict(),
        reason=f"User {current_user.email} created patient",
    )
    
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        name=patient.name,
        date_of_birth=patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        created_by=patient.created_by,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get patient by ID."""
    
    repo = PatientRepository(db)
    patient = repo.get(patient_id)
    
    if not patient:
        raise ResourceNotFound("Patient", patient_id)
    
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        name=patient.name,
        date_of_birth=patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        created_by=patient.created_by,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )
