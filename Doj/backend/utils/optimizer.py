import math
from typing import List, Tuple, Dict
import gurobipy as gp
from gurobipy import GRB
from models import Technician, Task, TechnicianRoute, OptimizedTask, Location

def calculate_distance(coord1: Location, coord2: Location) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lng1 = math.radians(coord1.lat), math.radians(coord1.lng)
    lat2, lng2 = math.radians(coord2.lat), math.radians(coord2.lng)
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def optimize_routes_with_gurobi(technicians: List[Technician], tasks: List[Task]) -> List[TechnicianRoute]:

    if not technicians or not tasks:
        return []
    
    # Filter available technicians
    available_techs = [t for t in technicians if t.available]
    if not available_techs:
        return []
    
    # Priority weights
    priority_weight = {"high": 3, "medium": 2, "low": 1}
    
    try:
        # Create model
        model = gp.Model("MaintenanceRouting")
        model.setParam('OutputFlag', 0)  # Suppress output
        model.setParam('TimeLimit', 30)  # 30 seconds time limit
        
        n_tasks = len(tasks)
        n_techs = len(available_techs)
        
        # Decision variables: x[i,j] = 1 if task i assigned to technician j
        x = {}
        for i in range(n_tasks):
            for j in range(n_techs):
                # Only create variable if technician has required skill
                if tasks[i].requiredSkill in available_techs[j].skills:
                    x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")
        
        # Position variables: y[i,k,j] = 1 if task i is at position k for technician j
        y = {}
        for i in range(n_tasks):
            for j in range(n_techs):
                if (i, j) in x:  # Only if assignment is possible
                    for k in range(available_techs[j].maxTasksPerDay):
                        y[i, k, j] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}_{k}_{j}")
        
        model.update()
        print(f"[GUROBI] Created {len(x)} assignment variables and {len(y)} position variables")
        
        # Objective: Minimize total distance weighted by priority
        obj_expr = 0
        
        # 1. Reward assignments (Primary objective)
        # We want to MAXIMIZE assignments, so in MINIMIZE objective, we subtract a large value
        ASSIGNMENT_REWARD = 100000
        
        for i in range(n_tasks):
            for j in range(n_techs):
                if (i, j) in x:
                    # Base reward for any assignment + bonus for priority
                    prio_bonus = priority_weight[tasks[i].priority] * 1000
                    obj_expr -= x[i, j] * (ASSIGNMENT_REWARD + prio_bonus)
        
        # 2. Minimize distance (Secondary objective)
        for j in range(n_techs):
            tech_loc = available_techs[j].location
            
            for i in range(n_tasks):
                if (i, j) not in x:
                    continue
                
                task_loc = tasks[i].location
                priority_multiplier = 4 - priority_weight[tasks[i].priority]  # Invert for minimization
                
                # Distance from technician start to first task (position 0)
                if (i, 0, j) in y:
                    dist = calculate_distance(tech_loc, task_loc)
                    obj_expr += dist * y[i, 0, j] * priority_multiplier
                
                # Distance between consecutive tasks
                for k in range(1, available_techs[j].maxTasksPerDay):
                    if (i, k, j) not in y:
                        continue
                    
                    for i2 in range(n_tasks):
                        if i2 == i or (i2, k-1, j) not in y:
                            continue
                        
                        dist = calculate_distance(tasks[i2].location, task_loc)
                        # Link: if task i2 at position k-1 and task i at position k
                        obj_expr += dist * y[i2, k-1, j] * y[i, k, j] * priority_multiplier
        
        model.setObjective(obj_expr, GRB.MINIMIZE)
        
        # Constraint 1: Each task assigned to at most one technician
        for i in range(n_tasks):
            expr = gp.LinExpr()
            for j in range(n_techs):
                if (i, j) in x:
                    expr += x[i, j]
            model.addConstr(expr <= 1, f"task_assignment_{i}")
        
        # Constraint 2: Task assignment matches position assignment
        for i in range(n_tasks):
            for j in range(n_techs):
                if (i, j) not in x:
                    continue
                
                expr = gp.LinExpr()
                for k in range(available_techs[j].maxTasksPerDay):
                    if (i, k, j) in y:
                        expr += y[i, k, j]
                
                model.addConstr(expr == x[i, j], f"position_match_{i}_{j}")
        
        # Constraint 3: Each position used at most once per technician
        for j in range(n_techs):
            for k in range(available_techs[j].maxTasksPerDay):
                expr = gp.LinExpr()
                for i in range(n_tasks):
                    if (i, k, j) in y:
                        expr += y[i, k, j]
                model.addConstr(expr <= 1, f"position_unique_{k}_{j}")
        
        # Constraint 4: Positions must be consecutive (no gaps)
        for j in range(n_techs):
            for k in range(1, available_techs[j].maxTasksPerDay):
                # If position k is used, position k-1 must be used
                expr_k = gp.LinExpr()
                expr_k_prev = gp.LinExpr()
                
                for i in range(n_tasks):
                    if (i, k, j) in y:
                        expr_k += y[i, k, j]
                    if (i, k-1, j) in y:
                        expr_k_prev += y[i, k-1, j]
                
                model.addConstr(expr_k <= expr_k_prev, f"consecutive_{k}_{j}")
        
        # Optimize
        model.optimize()
        
        print(f"[GUROBI] Model status: {model.status}")
        if model.status == GRB.OPTIMAL:
            print(f"[GUROBI] Optimal solution found! Obj: {model.objVal}")
        elif model.status == GRB.INFEASIBLE:
            print("[GUROBI] Model is infeasible")
            model.computeIIS()
            model.write("model.ilp")
        
        # Extract solution
        routes = []
        
        if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
            for j in range(n_techs):
                tech = available_techs[j]
                assigned_tasks = []
                
                # Get tasks in order by position
                for k in range(tech.maxTasksPerDay):
                    for i in range(n_tasks):
                        if (i, k, j) in y and y[i, k, j].X > 0.5:
                            task = tasks[i]
                            
                            # Calculate distance from previous position
                            dist_from_prev = 0
                            if k == 0:
                                dist_from_prev = calculate_distance(tech.location, task.location)
                            else:
                                # Find previous task
                                for i_prev in range(n_tasks):
                                    if (i_prev, k-1, j) in y and y[i_prev, k-1, j].X > 0.5:
                                        dist_from_prev = calculate_distance(
                                            tasks[i_prev].location, 
                                            task.location
                                        )
                                        break
                            
                            optimized_task = OptimizedTask(
                                id=task.id,
                                title=task.title,
                                description=task.description,
                                requiredSkill=task.requiredSkill,
                                priority=task.priority,
                                duration=task.duration,
                                location=task.location,
                                distanceFromPrevious=round(dist_from_prev, 2)
                            )
                            assigned_tasks.append(optimized_task)
                            break
                
                if assigned_tasks:
                    total_distance = sum(t.distanceFromPrevious for t in assigned_tasks if t.distanceFromPrevious)
                    total_duration = sum(t.duration for t in assigned_tasks)
                    
                    route = TechnicianRoute(
                        technicianId=tech.id,
                        technicianName=tech.name,
                        tasks=assigned_tasks,
                        totalDistance=round(total_distance, 2),
                        totalDuration=total_duration,
                        taskCount=len(assigned_tasks)
                    )
                    routes.append(route)
        
        return routes
        
    except gp.GurobiError as e:
        print(f"Gurobi error (using greedy fallback): {e}")
        # Fallback to greedy algorithm if Gurobi fails
        return optimize_routes_greedy(technicians, tasks)
    except Exception as e:
        print(f"Optimization error (using greedy fallback): {e}")
        import traceback
        traceback.print_exc()
        return optimize_routes_greedy(technicians, tasks)

def optimize_routes_greedy(technicians: List[Technician], tasks: List[Task]) -> List[TechnicianRoute]:
    """
    Fallback greedy algorithm for route optimization
    """
    print(f"[GREEDY] Starting with {len(technicians)} technicians and {len(tasks)} tasks")
    routes = []
    available_techs = [t for t in technicians if t.available]
    
    print(f"[GREEDY] Available technicians: {len(available_techs)}")
    if not available_techs or not tasks:
        print(f"[GREEDY] No available techs or tasks - returning empty")
        return []
    
    # Sort tasks by priority
    priority_map = {"high": 3, "medium": 2, "low": 1}
    sorted_tasks = sorted(tasks, key=lambda t: priority_map[t.priority], reverse=True)
    
    # Assign tasks to technicians
    tech_tasks: Dict[str, List[Task]] = {tech.id: [] for tech in available_techs}
    
    for task in sorted_tasks:
        print(f"[GREEDY] Assigning task '{task.title}' (skill: {task.requiredSkill})")
        # Find qualified technicians sorted by distance
        qualified = [
            (tech, calculate_distance(tech.location, task.location))
            for tech in available_techs
            if task.requiredSkill in tech.skills and len(tech_tasks[tech.id]) < tech.maxTasksPerDay
        ]
        
        print(f"[GREEDY] Found {len(qualified)} qualified technicians for this task")
        if qualified:
            qualified.sort(key=lambda x: x[1])
            assigned_tech = qualified[0][0]
            tech_tasks[assigned_tech.id].append(task)
            print(f"[GREEDY] Assigned to {assigned_tech.name}")
    
    # Optimize route for each technician using nearest neighbor
    print(f"[GREEDY] Creating routes...")
    for tech in available_techs:
        if not tech_tasks[tech.id]:
            print(f"[GREEDY] No tasks for {tech.name}")
            continue
        print(f"[GREEDY] Creating route for {tech.name} with {len(tech_tasks[tech.id])} tasks")
        
        # Nearest neighbor optimization
        route_tasks = []
        remaining = tech_tasks[tech.id].copy()
        current_loc = tech.location
        
        while remaining:
            # Find nearest task
            nearest_idx = 0
            min_dist = calculate_distance(current_loc, remaining[0].location)
            
            for i in range(1, len(remaining)):
                dist = calculate_distance(current_loc, remaining[i].location)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i
            
            task = remaining.pop(nearest_idx)
            optimized_task = OptimizedTask(
                id=task.id,
                title=task.title,
                description=task.description,
                requiredSkill=task.requiredSkill,
                priority=task.priority,
                duration=task.duration,
                location=task.location,
                distanceFromPrevious=round(min_dist, 2)
            )
            route_tasks.append(optimized_task)
            current_loc = task.location
        
        total_distance = sum(t.distanceFromPrevious for t in route_tasks if t.distanceFromPrevious)
        total_duration = sum(t.duration for t in route_tasks)
        
        route = TechnicianRoute(
            technicianId=tech.id,
            technicianName=tech.name,
            tasks=route_tasks,
            totalDistance=round(total_distance, 2),
            totalDuration=total_duration,
            taskCount=len(route_tasks)
        )
        routes.append(route)
    
    print(f"[GREEDY] Completed! Generated {len(routes)} routes")
    return routes