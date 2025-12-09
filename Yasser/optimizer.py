import gurobipy as gp
from gurobipy import GRB

class ProductionOptimizer:
    def __init__(self, markets, sites, costs_matrix):
        """
        markets: list of dict [{'id': 0, 'demand': 100, 'x': 0, 'y': 0}, ...]
        sites: list of dict [{'id': 0, 'capacity': 500, 'fixed_cost': 1000, 'x': 5, 'y': 5}, ...]
        costs_matrix: 2D array/list where cost[site_idx][market_idx] = transport cost
        """
        self.markets = markets
        self.sites = sites
        self.costs_matrix = costs_matrix
        self.model = None
        self.status = ""

    def solve(self):
        try:
            # 1. Création du modèle
            m = gp.Model("Production_Location_Allocation")
            m.setParam('OutputFlag', 0) # Désactiver les logs console de Gurobi

            num_markets = len(self.markets)
            num_sites = len(self.sites)

            # 2. Variables de décision
            # y[j] = 1 si l'usine j est ouverte
            y = m.addVars(num_sites, vtype=GRB.BINARY, name="Open")
            
            # x[j, i] = quantité transportée de j vers i
            x = m.addVars(num_sites, num_markets, vtype=GRB.CONTINUOUS, name="Flow")

            # 3. Fonction Objectif : Min (Coûts fixes + Coûts transport)
            setup_cost = gp.quicksum(site['fixed_cost'] * y[j] for j, site in enumerate(self.sites))
            transport_cost = gp.quicksum(self.costs_matrix[j][i] * x[j, i] 
                                         for j in range(num_sites) 
                                         for i in range(num_markets))
            
            m.setObjective(setup_cost + transport_cost, GRB.MINIMIZE)

            # 4. Contraintes
            
            # C1: Satisfaction de la demande pour chaque marché
            for i, market in enumerate(self.markets):
                m.addConstr(gp.quicksum(x[j, i] for j in range(num_sites)) == market['demand'], 
                            name=f"Demand_{i}")

            # C2: Respect de la capacité (et lien logique : si fermé, cap = 0)
            for j, site in enumerate(self.sites):
                m.addConstr(gp.quicksum(x[j, i] for i in range(num_markets)) <= site['capacity'] * y[j], 
                            name=f"Capacity_{j}")

            # 5. Résolution
            m.optimize()

            # 6. Extraction des résultats
            if m.Status == GRB.OPTIMAL:
                results = {
                    'status': 'Optimal',
                    'obj_val': m.ObjVal,
                    'sites_open': [],
                    'flows': []
                }
                
                # Récupérer quelles usines sont ouvertes
                for j in range(num_sites):
                    if y[j].X > 0.5: # Si proche de 1
                        results['sites_open'].append(j)
                        
                # Récupérer les flux non nuls
                for j in range(num_sites):
                    for i in range(num_markets):
                        if x[j, i].X > 0.001:
                            results['flows'].append({
                                'factory_idx': j,
                                'market_idx': i,
                                'qty': x[j, i].X
                            })
                return results
            else:
                return {'status': 'Infeasible/Unbounded', 'obj_val': 0}

        except gp.GurobiError as e:
            return {'status': f"Error: {e.errno} - {e.message}"}
        except Exception as e:
            return {'status': f"Exception: {str(e)}"}