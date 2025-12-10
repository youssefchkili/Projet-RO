from typing import List, Dict, Optional
from models import Technician, Task, TechnicianCreate, TaskCreate
from datetime import datetime

# In-memory storage
_technicians: Dict[str, Technician] = {}
_tasks: Dict[str, Task] = {}
_routes: List[dict] = []

# Initialize with sample data
def initialize_data():
    global _technicians, _tasks
    
    sample_technicians = [
        TechnicianCreate(
            name="Jean Dupont",
            skills=["plomberie", "électricité"],
            available=True,
            maxTasksPerDay=5,
            location={"lat": 48.8566, "lng": 2.3522, "address": ""}
        ),
        TechnicianCreate(
            name="Marie Martin",
            skills=["électricité", "climatisation"],
            available=True,
            maxTasksPerDay=6,
            location={"lat": 48.8606, "lng": 2.3376, "address": ""}
        ),
        TechnicianCreate(
            name="Pierre Dubois",
            skills=["plomberie", "chauffage"],
            available=True,
            maxTasksPerDay=5,
            location={"lat": 48.8534, "lng": 2.3488, "address": ""}
        )
    ]
    
    for i, tech_data in enumerate(sample_technicians, 1):
        tech = Technician(id=str(i), **tech_data.model_dump())
        _technicians[tech.id] = tech
    
    sample_tasks = [
        TaskCreate(
            title="Réparation fuite d'eau",
            description="Fuite sous l'évier de la cuisine",
            requiredSkill="plomberie",
            priority="high",
            duration=60,
            location={"lat": 48.8584, "lng": 2.2945, "address": "15 Rue de la Pompe, Paris"}
        ),
        TaskCreate(
            title="Installation climatiseur",
            description="Installation d'un nouveau climatiseur",
            requiredSkill="climatisation",
            priority="medium",
            duration=120,
            location={"lat": 48.8738, "lng": 2.2950, "address": "45 Avenue Victor Hugo, Paris"}
        ),
        TaskCreate(
            title="Problème électrique",
            description="Disjoncteur qui saute régulièrement",
            requiredSkill="électricité",
            priority="high",
            duration=90,
            location={"lat": 48.8462, "lng": 2.3372, "address": "23 Boulevard Saint-Michel, Paris"}
        ),
        TaskCreate(
            title="Entretien chaudière",
            description="Entretien annuel de la chaudière",
            requiredSkill="chauffage",
            priority="low",
            duration=60,
            location={"lat": 48.8700, "lng": 2.3400, "address": "10 Rue de Provence, Paris"}
        )
    ]
    
    for i, task_data in enumerate(sample_tasks, 1):
        task = Task(id=str(i), status="pending", assignedTo=None, **task_data.model_dump())
        _tasks[task.id] = task

# Initialize data on module import
initialize_data()

# Technician operations
def get_all_technicians() -> List[Technician]:
    return list(_technicians.values())

def get_technician_by_id(tech_id: str) -> Optional[Technician]:
    return _technicians.get(tech_id)

def create_technician(technician: TechnicianCreate) -> Technician:
    tech_id = str(int(datetime.now().timestamp() * 1000))
    tech = Technician(id=tech_id, **technician.model_dump())
    _technicians[tech_id] = tech
    return tech

def update_technician(tech_id: str, update_data: dict) -> Optional[Technician]:
    if tech_id not in _technicians:
        return None
    
    tech = _technicians[tech_id]
    for key, value in update_data.items():
        if value is not None and hasattr(tech, key):
            setattr(tech, key, value)
    
    return tech

def delete_technician(tech_id: str) -> bool:
    if tech_id in _technicians:
        del _technicians[tech_id]
        return True
    return False

# Task operations
def get_all_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> List[Task]:
    tasks = list(_tasks.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    
    return tasks

def get_task_by_id(task_id: str) -> Optional[Task]:
    return _tasks.get(task_id)

def create_task(task: TaskCreate) -> Task:
    task_id = str(int(datetime.now().timestamp() * 1000))
    new_task = Task(id=task_id, status="pending", assignedTo=None, **task.model_dump())
    _tasks[task_id] = new_task
    return new_task

def update_task(task_id: str, update_data: dict) -> Optional[Task]:
    if task_id not in _tasks:
        return None
    
    task = _tasks[task_id]
    for key, value in update_data.items():
        if value is not None and hasattr(task, key):
            setattr(task, key, value)
    
    return task

def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False

# Route operations
def get_all_routes() -> List[dict]:
    return _routes

def save_route(route: dict) -> dict:
    route_id = str(int(datetime.now().timestamp() * 1000))
    route["id"] = route_id
    route["createdAt"] = datetime.now().isoformat()
    _routes.append(route)
    return route

def clear_routes():
    global _routes
    _routes = []
