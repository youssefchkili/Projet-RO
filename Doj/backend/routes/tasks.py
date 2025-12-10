from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import Task, TaskCreate, TaskUpdate
from data import storage

router = APIRouter()

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    """Get all tasks with optional filters"""
    return storage.get_all_tasks(status=status, priority=priority)

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get task by ID"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    """Create new task"""
    if not task.title or not task.requiredSkill or not task.location:
        raise HTTPException(
            status_code=400, 
            detail="Title, required skill, and location are required"
        )
    return storage.create_task(task)

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, update_data: TaskUpdate):
    """Update task"""
    update_dict = update_data.model_dump(exclude_unset=True)
    updated = storage.update_task(task_id, update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete task"""
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
