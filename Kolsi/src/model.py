import gurobipy as gp
from gurobipy import GRB
from dataclasses import dataclass

@dataclass
class ArcData:
    source: str
    target: str
    capacity: float
    var_cost: float
    fixed_cost: float

@dataclass
class CommodityData:
    cid: str
    origin: str
    destination: str
    quantity: float
    quality_name: str
    color: str 

class GasOptimizationModel:
    def solve_model(self, arcs: list[ArcData], commodities: list[CommodityData]):
        try:
            # 1. Setup Data
            nodes = set()
            arc_keys = []
            capacity = {}
            var_cost = {}
            fixed_cost = {}
            
            for a in arcs:
                nodes.add(a.source)
                nodes.add(a.target)
                key = (a.source, a.target)
                arc_keys.append(key)
                capacity[key] = a.capacity
                var_cost[key] = a.var_cost
                fixed_cost[key] = a.fixed_cost

            comm_ids = [c.cid for c in commodities]
            comm_info = {c.cid: (c.origin, c.destination, c.quantity) for c in commodities}

            # 2. Model (Mixed Integer Programming)
            m = gp.Model("GasMultiQuality_MCNF")
            m.Params.OutputFlag = 0 
            
            # Variables
            # y = Binary (1 if pipe is open, 0 if closed) -> This makes it a PLNE/PLM problem
            y = m.addVars(arc_keys, vtype=GRB.BINARY, name="use")
            # x = Continuous (Flow amount)
            x = m.addVars(arc_keys, comm_ids, vtype=GRB.CONTINUOUS, lb=0.0, name="flow")

            # Objective: Min (Fixed Costs * y) + (Variable Costs * x)
            fixed_obj = y.prod(fixed_cost)
            var_obj = gp.quicksum(x[i, j, k] * var_cost[i, j] for i, j in arc_keys for k in comm_ids)
            m.setObjective(fixed_obj + var_obj, GRB.MINIMIZE)

            # Constraints
            # 1. Capacity: Sum of ALL gas qualities <= Capacity * BinaryOpen
            for i, j in arc_keys:
                m.addConstr(x.sum(i, j, '*') <= capacity[i, j] * y[i, j], name=f"Cap_{i}_{j}")

            # 2. Flow Conservation (Kirchhoff's Law for each Gas Quality)
            for k in comm_ids:
                origin, dest, qty = comm_info[k]
                for n in nodes:
                    inflow = x.sum('*', n, k)
                    outflow = x.sum(n, '*', k)
                    if n == origin:
                        m.addConstr(outflow - inflow == qty, name=f"Bal_{n}_{k}_Sup")
                    elif n == dest:
                        m.addConstr(inflow - outflow == qty, name=f"Bal_{n}_{k}_Dem")
                    else:
                        m.addConstr(inflow == outflow, name=f"Bal_{n}_{k}_Trans")

            m.optimize()

            if m.status == GRB.OPTIMAL:
                return True, m.objVal, self._extract_results(x, y)
            else:
                return False, 0.0, None

        except gp.GurobiError as e:
            return False, 0.0, str(e)

    def _extract_results(self, x, y):
        results = {
            'flows': [],
            'active_pipes': []
        }
        for (u, v), var in y.items():
            if var.X > 0.5:
                results['active_pipes'].append((u, v))
        for (u, v, k), var in x.items():
            if var.X > 1e-4:
                results['flows'].append({
                    'source': u, 'target': v, 'commodity': k, 'amount': var.X
                })
        return results