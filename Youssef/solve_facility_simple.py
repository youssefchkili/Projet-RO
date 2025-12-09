# solve_facility_simple.py
"""
Modèle simplifié de localisation d'hôpitaux - PLNE
Version simplifiée mais complète pour projet RO
"""
import numpy as np
from gurobipy import Model, GRB, quicksum


def generate_instance(n_customers=10, m_sites=5, seed=1):
    """
    Génère une instance du problème de localisation d'hôpitaux
    
    Paramètres retournés:
    - Coordonnées géographiques des villes et sites
    - Demande (nombre de patients) par ville
    - Coûts fixes d'ouverture par site
    - Capacités des sites
    - Distances entre villes et sites
    - Budget disponible
    """
    rng = np.random.RandomState(seed)
    
    # Coordonnées géographiques (en km)
    cust_coords = rng.rand(n_customers, 2) * 100
    site_coords = rng.rand(m_sites, 2) * 100
    
    # PARAMÈTRE 1: Demande (nombre de patients par ville)
    demand = rng.randint(10, 50, size=n_customers)
    
    # PARAMÈTRE 2: Coûts fixes d'ouverture (varient selon le site)
    fixed_cost = rng.randint(5000, 15000, size=m_sites)
    
    # PARAMÈTRE 3: Capacités des sites (nombre max de patients)
    total_demand = demand.sum()
    capacity = rng.randint(30, 80, size=m_sites)
    
    # Assurer faisabilité: capacité totale >= demande totale
    if capacity.sum() < total_demand:
        factor = int(np.ceil(total_demand / capacity.sum())) + 1
        capacity = capacity * factor
    
    # PARAMÈTRE 4: Distances euclidiennes (en km)
    distances = np.linalg.norm(
        cust_coords[:, None, :] - site_coords[None, :, :], 
        axis=2
    )
    
    # PARAMÈTRE 5: Coût de transport par km par patient
    transport_cost_per_km = 2.5
    
    # PARAMÈTRE 6: Niveaux de qualité des sites (0-100)
    quality = rng.randint(40, 95, size=m_sites)
    
    # PARAMÈTRE 7: Distance maximale autorisée (contrainte de service)
    max_distance = 60.0  # km
    
    # PARAMÈTRE 8: Budget disponible (calculé pour faisabilité)
    min_sites_needed = int(np.ceil(total_demand / capacity.max()))
    sorted_costs = np.sort(fixed_cost)
    min_budget = sorted_costs[:min_sites_needed].sum()
    budget = min_budget * 1.8  # 80% de marge
    
    return {
        'cust_coords': cust_coords,
        'site_coords': site_coords,
        'demand': demand,
        'fixed_cost': fixed_cost,
        'capacity': capacity,
        'distances': distances,
        'transport_cost': transport_cost_per_km,
        'quality': quality,
        'max_distance': max_distance,
        'budget': budget,
        'n_customers': n_customers,
        'm_sites': m_sites
    }


def solve_instance(instance, time_limit=60, mip_gap=0.01, alpha=0.7, beta=0.3):
    """
    Résout le problème de localisation avec Gurobi
    
    MODÉLISATION PLNE:
    
    Variables de décision:
    - y[j] ∈ {0,1} : 1 si l'hôpital j est ouvert
    - x[i,j] ∈ {0,1} : 1 si la ville i est affectée à l'hôpital j
    
    Fonction objectif:
    MIN: α * (Coûts fixes + Coûts transport) - β * Qualité totale
    
    Contraintes:
    1. Chaque ville affectée à exactement un hôpital
    2. Capacité: demande affectée ≤ capacité * ouverture
    3. Distance maximale: distance ≤ max_distance si affecté
    4. Budget: somme coûts fixes ≤ budget
    5. Lien logique: affectation => ouverture
    
    Paramètres:
    - alpha: poids du coût (défaut 0.7)
    - beta: poids de la qualité (défaut 0.3)
    """
    
    # Extraction des données
    n = instance['n_customers']
    m = instance['m_sites']
    demand = instance['demand']
    fixed_cost = instance['fixed_cost']
    capacity = instance['capacity']
    dist = instance['distances']
    transport_cost = instance['transport_cost']
    quality = instance['quality']
    max_dist = instance['max_distance']
    budget = instance['budget']
    
    # Créer le modèle
    model = Model("hospital_location")
    model.setParam('OutputFlag', 0)
    model.setParam('TimeLimit', time_limit)
    model.setParam('MIPGap', mip_gap)
    
    # VARIABLES
    y = model.addVars(m, vtype=GRB.BINARY, name="y")  # Ouverture
    x = model.addVars(n, m, vtype=GRB.BINARY, name="x")  # Affectation
    
    # OBJECTIF
    # Coûts
    cost_fixed = quicksum(fixed_cost[j] * y[j] for j in range(m))
    cost_transport = quicksum(
        demand[i] * dist[i, j] * transport_cost * x[i, j]
        for i in range(n) for j in range(m)
    )
    total_cost = cost_fixed + cost_transport
    
    # Qualité (à maximiser)
    total_quality = quicksum(
        quality[j] * demand[i] * x[i, j]
        for i in range(n) for j in range(m)
    )
    
    # Objectif pondéré
    model.setObjective(
        alpha * total_cost - beta * total_quality,
        GRB.MINIMIZE
    )
    
    # CONTRAINTES
    
    # C1: Chaque ville affectée à exactement un hôpital
    model.addConstrs(
        (quicksum(x[i, j] for j in range(m)) == 1 for i in range(n)),
        name="assign"
    )
    
    # C2: Capacité
    model.addConstrs(
        (quicksum(demand[i] * x[i, j] for i in range(n)) <= capacity[j] * y[j]
         for j in range(m)),
        name="capacity"
    )
    
    # C3: Distance maximale
    model.addConstrs(
        (dist[i, j] * x[i, j] <= max_dist for i in range(n) for j in range(m)),
        name="max_distance"
    )
    
    # C4: Budget
    model.addConstr(
        quicksum(fixed_cost[j] * y[j] for j in range(m)) <= budget,
        name="budget"
    )
    
    # C5: Lien logique (affectation => ouverture)
    model.addConstrs(
        (x[i, j] <= y[j] for i in range(n) for j in range(m)),
        name="link"
    )
    
    # RÉSOLUTION
    model.optimize()
    
    # EXTRACTION RÉSULTATS
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        y_sol = [int(y[j].x + 0.5) for j in range(m)]
        x_sol = [[int(x[i, j].x + 0.5) for j in range(m)] for i in range(n)]
        
        opened_sites = [j for j in range(m) if y_sol[j] == 1]
        
        # Calculs détaillés
        fixed_cost_val = sum(fixed_cost[j] for j in opened_sites)
        transport_cost_val = sum(
            demand[i] * dist[i, j] * transport_cost * x_sol[i][j]
            for i in range(n) for j in range(m)
        )
        
        avg_quality = sum(
            quality[j] * x_sol[i][j] for i in range(n) for j in range(m)
        ) / n if n > 0 else 0
        
        distances_list = []
        for i in range(n):
            for j in range(m):
                if x_sol[i][j] == 1:
                    distances_list.append(dist[i, j])
        
        avg_distance = np.mean(distances_list) if distances_list else 0
        max_distance_real = max(distances_list) if distances_list else 0
        
        capacity_usage = []
        for j in opened_sites:
            used = sum(demand[i] * x_sol[i][j] for i in range(n))
            capacity_usage.append(used / capacity[j] if capacity[j] > 0 else 0)
        
        return {
            "status": model.status,
            "objective": model.ObjVal,
            "y": y_sol,
            "x": x_sol,
            "opened_sites": opened_sites,
            "n_opened": len(opened_sites),
            "fixed_cost": fixed_cost_val,
            "transport_cost": transport_cost_val,
            "total_cost": fixed_cost_val + transport_cost_val,
            "avg_quality": avg_quality,
            "avg_distance": avg_distance,
            "max_distance": max_distance_real,
            "capacity_usage": capacity_usage,
            "avg_capacity": np.mean(capacity_usage) if capacity_usage else 0,
            "gap": model.MIPGap if hasattr(model, 'MIPGap') else 0,
            "runtime": model.Runtime
        }
    else:
        return {"status": model.status, "objective": None}


if __name__ == "__main__":
    print("="*60)
    print("TEST - LOCALISATION D'HÔPITAUX (Modèle Simplifié)")
    print("="*60)
    
    instance = generate_instance(12, 5, seed=42)
    
    print(f"\nInstance: {instance['n_customers']} villes, {instance['m_sites']} sites")
    print(f"Demande totale: {instance['demand'].sum()} patients")
    print(f"Capacité totale: {instance['capacity'].sum()}")
    print(f"Budget: {instance['budget']:.2f} €")
    
    print("\n" + "="*60)
    print("RÉSOLUTION")
    print("="*60)
    
    result = solve_instance(instance, time_limit=30)
    
    if result.get('objective') is None:
        print("❌ Problème non résolu")
    else:
        print(f"✅ Solution optimale trouvée!")
        print(f"\nObjectif total: {result['objective']:.2f}")
        print(f"Hôpitaux ouverts: {result['n_opened']}/{instance['m_sites']}")
        print(f"\nCoûts:")
        print(f"  - Fixes: {result['fixed_cost']:.2f} €")
        print(f"  - Transport: {result['transport_cost']:.2f} €")
        print(f"  - Total: {result['total_cost']:.2f} €")
        print(f"\nPerformance:")
        print(f"  - Qualité moyenne: {result['avg_quality']:.1f}")
        print(f"  - Distance moyenne: {result['avg_distance']:.1f} km")
        print(f"  - Distance max: {result['max_distance']:.1f} km")
        print(f"  - Taux capacité: {result['avg_capacity']*100:.1f}%")
        print(f"  - Gap: {result['gap']*100:.2f}%")
        print(f"  - Temps: {result['runtime']:.2f}s")
        
        print(f"\nSites ouverts: {result['opened_sites']}")
        print("\nAffectations:")
        for i in range(instance['n_customers']):
            for j in range(instance['m_sites']):
                if result['x'][i][j] == 1:
                    print(f"  Ville {i} ({instance['demand'][i]} pat.) → Hôpital {j} (qualité {instance['quality'][j]})")
