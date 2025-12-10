from fastapi import APIRouter, HTTPException
from typing import List
from models import Technician, TechnicianCreate, TechnicianUpdate
from data import storage

router = APIRouter()

@router.get("/", response_model=List[Technician])
async def get_technicians():
    """Get all technicians"""
    return storage.get_all_technicians()

@router.get("/{tech_id}", response_model=Technician)
async def get_technician(tech_id: str):
    """Get technician by ID"""
    tech = storage.get_technician_by_id(tech_id)
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")
    return tech

@router.post("/", response_model=Technician, status_code=201)
async def create_technician(technician: TechnicianCreate):
    """Create new technician"""
    if not technician.skills:
        raise HTTPException(status_code=400, detail="Skills are required")
    return storage.create_technician(technician)

@router.put("/{tech_id}", response_model=Technician)
async def update_technician(tech_id: str, update_data: TechnicianUpdate):
    """Update technician"""
    update_dict = update_data.model_dump(exclude_unset=True)
    updated = storage.update_technician(tech_id, update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Technician not found")
    return updated

@router.delete("/{tech_id}")
async def delete_technician(tech_id: str):
    """Delete technician"""
    deleted = storage.delete_technician(tech_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Technician not found")
    return {"message": "Technician deleted successfully"}
