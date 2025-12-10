from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Location(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = ""

class TechnicianBase(BaseModel):
    name: str
    skills: List[str]
    available: bool = True
    maxTasksPerDay: int = Field(default=5, ge=1, le=20)
    location: Location

class TechnicianCreate(TechnicianBase):
    pass

class TechnicianUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    available: Optional[bool] = None
    maxTasksPerDay: Optional[int] = None
    location: Optional[Location] = None

class Technician(TechnicianBase):
    id: str

    class Config:
        from_attributes = True

class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class TaskStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    completed = "completed"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    requiredSkill: str
    priority: Priority = Priority.medium
    duration: int = Field(default=60, ge=15)
    location: Location

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requiredSkill: Optional[str] = None
    priority: Optional[Priority] = None
    duration: Optional[int] = None
    location: Optional[Location] = None
    status: Optional[TaskStatus] = None
    assignedTo: Optional[str] = None

class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.pending
    assignedTo: Optional[str] = None

    class Config:
        from_attributes = True

class OptimizedTask(BaseModel):
    id: str
    title: str
    description: str
    requiredSkill: str
    priority: str
    duration: int
    location: Location
    distanceFromPrevious: Optional[float] = None

class TechnicianRoute(BaseModel):
    technicianId: str
    technicianName: str
    tasks: List[OptimizedTask]
    totalDistance: float
    totalDuration: int
    taskCount: int

class RouteOptimizationResult(BaseModel):
    id: str
    routes: List[TechnicianRoute]
    totalTasks: int
    assignedTasks: int
    createdAt: str
