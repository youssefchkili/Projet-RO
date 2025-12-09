# 🏥 Localisation d'Hôpitaux - Version Simplifiée
## Projet de Recherche Opérationnelle - PLNE

---

## 📋 Description

Application simplifiée de **Programmation Linéaire Mixte en Nombres Entiers (PLNE)** pour résoudre le problème de localisation optimale d'hôpitaux et d'allocation de patients.

**Version épurée** : Focus sur l'optimisation correcte avec les éléments essentiels uniquement.

---

## 🎯 Problème Résolu

**Objectif** : Déterminer quels sites candidats doivent être ouverts et comment affecter les patients de chaque ville aux hôpitaux de manière optimale.

**Critères** :
- Minimiser les coûts (fixes + transport)
- Maximiser la qualité de service
- Respecter les contraintes de capacité, distance et budget

---

## 🔧 Modélisation PLNE

### Variables de Décision
- **y[j] ∈ {0,1}** : 1 si l'hôpital j est ouvert, 0 sinon
- **x[i,j] ∈ {0,1}** : 1 si la ville i est affectée à l'hôpital j, 0 sinon

### Fonction Objectif
```
MIN: α × (Coûts fixes + Coûts transport) - β × Qualité totale
```
- α : poids du coût économique (défaut: 0.7)
- β : poids de la qualité de service (défaut: 0.3)

### Contraintes
1. **Affectation unique** : Chaque ville affectée à exactement un hôpital
2. **Capacité** : Demande affectée ≤ Capacité × Ouverture
3. **Distance maximale** : Distance ≤ 60 km pour les affectations
4. **Budget** : Somme des coûts fixes ≤ Budget disponible
5. **Lien logique** : Affectation possible uniquement si hôpital ouvert

### Paramètres (8 catégories)
1. Coordonnées géographiques (X, Y)
2. Demande (nombre de patients par ville)
3. Coûts fixes d'ouverture
4. Capacités des sites
5. Distances (euclidiennes)
6. Coût de transport (€/km/patient)
7. Niveaux de qualité (0-100)
8. Budget disponible

---

## 🚀 Installation

### Prérequis
- Python 3.8+
- Gurobi Optimizer (licence académique gratuite)
- PySide6
- NumPy
- Matplotlib

### Installation Rapide
```powershell
pip install numpy matplotlib PySide6 gurobipy
```

### Activer Licence Gurobi
```powershell
grbgetkey VOTRE-CLE-LICENCE
```

---

## 📂 Fichiers

```
Projet RO/
├── solve_facility_simple.py    # Modèle PLNE simplifié
├── gui_simple.py                # Interface graphique simplifiée
└── README_SIMPLE.md             # Ce fichier
```

---

## 🎮 Utilisation

### Méthode 1 : Ligne de Commande

```powershell
python solve_facility_simple.py
```

**Sortie attendue** :
```
Instance: 12 villes, 5 sites
Demande totale: 324 patients
Budget: 22690.80 €

✅ Solution optimale trouvée!
Objectif total: 22083.13
Hôpitaux ouverts: 2/5
Coûts: 41353.04 €
Temps: 0.04s
```

### Méthode 2 : Interface Graphique (Recommandé)

```powershell
python gui_simple.py
```

**Étapes** :
1. **Générer** : Cliquez sur "🎲 Générer" 
   - Ajustez nombre de villes (5-30)
   - Ajustez nombre de sites (3-15)

2. **Configurer** : Ajustez les paramètres
   - Temps limite : 10-300s (défaut: 60s)
   - Gap MIP : 0.1-10% (défaut: 1%)
   - α (Coût) : 0-1 (défaut: 0.7)
   - β (Qualité) : 0-1 (défaut: 0.3)

3. **Optimiser** : Cliquez sur "🚀 OPTIMISER"
   - Suivez la progression dans le journal
   - La solution s'affiche automatiquement

4. **Analyser** : Visualisez les résultats
   - Sites ouverts en vert
   - Sites fermés en gris
   - Lignes rouges = affectations
   - % = taux d'utilisation

---

## 📊 Résultats Typiques

Pour une instance 12×5 :

| Métrique | Valeur Typique |
|----------|----------------|
| Hôpitaux ouverts | 2-4 |
| Coût total | 30,000 - 50,000 € |
| Distance moyenne | 20-35 km |
| Taux de capacité | 70-90% |
| Temps de calcul | < 1 seconde |
| Gap MIP | < 1% |

---

## 🔍 Comprendre les Résultats

### Dans le Journal
```
✅ Solution trouvée!
📊 Objectif: 22083.13        ← Valeur fonction objectif
🏥 Ouverts: 2/5               ← Sites sélectionnés
💰 Coût: 41353.04 €           ← Coût total réel
⏱️ Temps: 0.04s               ← Temps de calcul
```

### Sur la Carte
- **Cercles bleus** : Villes (taille ∝ demande)
- **Carrés verts** : Hôpitaux ouverts
- **Carrés gris** : Sites non sélectionnés
- **Lignes rouges** : Affectations ville → hôpital
- **Annotations** : Taux d'utilisation des hôpitaux

---

## ⚙️ Paramètres d'Optimisation

### Time Limit (Temps Limite)
- **10-30s** : Test rapide
- **60s** : Bon compromis (défaut)
- **120-300s** : Solution de haute qualité

### MIP Gap (Tolérance)
- **0.1-0.5%** : Quasi-optimal (plus lent)
- **1%** : Excellent compromis (défaut)
- **5-10%** : Solution rapide

### Pondérations α et β

| Configuration | α | β | Résultat |
|---------------|---|---|----------|
| **Économique** | 1.0 | 0.0 | Coût minimal |
| **Équilibré** | 0.7 | 0.3 | Compromis (défaut) |
| **Qualité** | 0.3 | 0.7 | Service maximal |

---

## 🧪 Tests et Validation

### Test Rapide
```powershell
# Instance petite (rapide)
python solve_facility_simple.py
```

### Test Interface
```powershell
python gui_simple.py
```
1. Générer instance 8×4
2. Laisser paramètres par défaut
3. Cliquer Optimiser
4. Vérifier que solution s'affiche

### Validation
✅ Chaque ville affectée à exactement 1 hôpital  
✅ Capacités respectées  
✅ Budget respecté  
✅ Distances ≤ 60 km  
✅ Gap < 1%

---

## 🆘 Dépannage

### Problème : "No module named 'gurobipy'"
```powershell
pip install gurobipy
grbgetkey VOTRE-CLE
```

### Problème : "License expired"
Renouveler la licence sur https://www.gurobi.com/academia/

### Problème : Interface ne se lance pas
```powershell
pip install --upgrade PySide6
```

### Problème : Optimisation trop lente
- Réduire nombre de villes/sites
- Augmenter MIP Gap à 5%
- Réduire Time Limit

---

## 📚 Caractéristiques Techniques

### Complexité
- **Type** : PLNE (Programmation Linéaire Mixte en Nombres Entiers)
- **Variables** : m + n×m (binaires)
- **Contraintes** : n + m + n×m + 1 + n×m
- **Exemple 12×5** : 65 variables, 185 contraintes

### Performance
- **Solveur** : Gurobi Optimizer (Branch-and-Cut)
- **Temps typique** : < 1 seconde pour petites instances
- **Garantie** : Gap < 1% = solution à 99% de l'optimal

---

## 🎓 Points Forts

✅ **Modélisation correcte** : PLNE complet et valide  
✅ **8 paramètres** : Richesse suffisante  
✅ **5 contraintes** : Modèle réaliste  
✅ **Interface simple** : Facile à utiliser  
✅ **Visualisation claire** : Compréhension immédiate  
✅ **Multi-critères** : Coût + Qualité  
✅ **Optimisation rapide** : < 1s pour instances standard  
✅ **Code propre** : Bien commenté et structuré

---

## 📖 Pour Aller Plus Loin

### Extensions Possibles
1. Ajouter analyse de sensibilité
2. Export des résultats (CSV, PDF)
3. Import de données réelles
4. Plusieurs périodes de planification
5. Coûts d'exploitation annuels

### Littérature
- Daskin, M. S. (1995). "Network and Discrete Location"
- Facility Location Problem (Wikipedia)
- Gurobi Documentation

---

## 👥 Crédits

**Projet de Recherche Opérationnelle**  
**INSAT - Institut National des Sciences Appliquées et de Technologie**  
**Année : 2024-2025**

---

## 📄 Licence

Projet académique - INSAT

---

**Version** : 1.0 Simplifiée  
**Date** : Décembre 2025  
**Statut** : ✅ Prêt à l'emploi
