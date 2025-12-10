from fastapi import APIRouter, HTTPException
from typing import List
from models import RouteOptimizationResult, TaskStatus
from data import storage
from utils.optimizer import optimize_routes_with_gurobi

router = APIRouter()

@router.get("/", response_model=List[RouteOptimizationResult])
async def get_routes():
    """Get all saved routes"""
    return storage.get_all_routes()

@router.post("/optimize", response_model=RouteOptimizationResult)
async def optimize_routes():
    """Optimize and create routes using Gurobi MILP solver"""
    all_techs = storage.get_all_technicians()
    all_tasks = storage.get_all_tasks()
    
    print(f"[OPTIMIZE] Total technicians: {len(all_techs)}")
    print(f"[OPTIMIZE] Total tasks: {len(all_tasks)}")
    
    # Debug task statuses
    for t in all_tasks:
        print(f"[DEBUG] Task {t.id} ({t.title}): status='{t.status}' type={type(t.status)}")

    technicians = [t for t in all_techs if t.available]
    
    # Robust filtering for pending tasks
    tasks = []
    for t in all_tasks:
        # Check if status is pending (handling Enum, string, etc.)
        is_pending = (
            t.status == "pending" or 
            t.status == TaskStatus.pending or 
            str(t.status) == "pending" or
            str(t.status) == "TaskStatus.pending"
        )
        if is_pending:
            tasks.append(t)
    
    print(f"[OPTIMIZE] Available technicians: {len(technicians)}")
    print(f"[OPTIMIZE] Pending tasks: {len(tasks)}")
    
    if not technicians:
        raise HTTPException(status_code=400, detail="No available technicians")
    
    if not tasks:
        raise HTTPException(status_code=400, detail="No pending tasks")
    
    # Run Gurobi optimization
    print(f"[OPTIMIZE] Starting optimization...")
    optimized_routes = optimize_routes_with_gurobi(technicians, tasks)
    print(f"[OPTIMIZE] Optimization returned {len(optimized_routes)} routes")
    
    # Update task assignments
    for route in optimized_routes:
        for task in route.tasks:
            storage.update_task(task.id, {
                "assignedTo": route.technicianId,
                "status": "assigned"
            })
    
    # Save route result
    route_data = {
        "routes": [route.model_dump() for route in optimized_routes],
        "totalTasks": len(tasks),
        "assignedTasks": sum(route.taskCount for route in optimized_routes)
    }
    
    saved_route = storage.save_route(route_data)
    return saved_route

@router.delete("/")
async def clear_routes():
    """Clear all routes and reset task assignments"""
    storage.clear_routes()
    
    # Reset all assigned tasks to pending
    tasks = storage.get_all_tasks()
    for task in tasks:
        if task.status == "assigned":
            storage.update_task(task.id, {
                "assignedTo": None,
                "status": "pending"
            })
    
    return {"message": "All routes cleared and tasks reset"}
