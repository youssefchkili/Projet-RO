# MODÉLISATION MATHÉMATIQUE
## Problème de Localisation et Allocation d'Hôpitaux (PLNE Avancé)

---

## 1. DESCRIPTION DU PROBLÈME

Le problème consiste à déterminer :
1. **Quels sites candidats** doivent être ouverts pour y construire des hôpitaux
2. **Comment affecter** les patients de chaque ville aux hôpitaux ouverts

L'objectif est d'optimiser simultanément plusieurs critères :
- Minimiser les **coûts totaux** (fixes, exploitation, transport)
- Maximiser la **qualité de service** (spécialisation des hôpitaux)
- Garantir l'**équité** (limiter les distances excessives)

---

## 2. ENSEMBLES ET INDICES

- **I** : Ensemble des villes (clients) avec |I| = n
  - i ∈ I représente une ville i
  
- **J** : Ensemble des sites candidats pour les hôpitaux avec |J| = m
  - j ∈ J représente un site candidat j

---

## 3. PARAMÈTRES

### 3.1 Paramètres Géographiques
- **coord_i = (x_i, y_i)** : Coordonnées géographiques de la ville i (en km)
- **coord_j = (x_j, y_j)** : Coordonnées du site candidat j (en km)
- **d_ij** : Distance euclidienne entre la ville i et le site j (en km)
  - Calculée comme : d_ij = √[(x_i - x_j)² + (y_i - y_j)²]

### 3.2 Paramètres de Demande (par ville)
- **w_i^u** : Nombre de patients urgents dans la ville i
- **w_i^n** : Nombre de patients normaux dans la ville i
- **w_i** : Total de patients = w_i^u + w_i^n

### 3.3 Paramètres de Coûts
- **f_j** : Coût fixe d'ouverture de l'hôpital j (en €)
- **o_j** : Coût d'exploitation annuel de l'hôpital j (en €)
- **c_u** : Coût de transport par km par patient urgent (€/km/patient)
- **c_n** : Coût de transport par km par patient normal (€/km/patient)

### 3.4 Paramètres de Capacité
- **cap_j^u** : Capacité maximale pour patients urgents de l'hôpital j
- **cap_j^n** : Capacité maximale pour patients normaux de l'hôpital j

### 3.5 Paramètres de Qualité
- **spec_j** : Niveau de spécialisation de l'hôpital j ∈ {0, 1, 2, 3}
  - 0 : Basique
  - 1 : Standard
  - 2 : Avancé
  - 3 : Excellence
- **q_j** : Score de qualité globale de l'hôpital j

### 3.6 Contraintes de Service
- **D_max^u** : Distance maximale autorisée pour patients urgents (en km)
- **D_max^n** : Distance maximale autorisée pour patients normaux (en km)
- **B** : Budget total disponible (en €)

### 3.7 Pondérations Multi-critères
- **α** : Poids du critère économique (coûts) - défaut : 0.7
- **β** : Poids du critère qualité de service - défaut : 0.2
- **γ** : Poids du critère équité (pénalités distance) - défaut : 0.1
- **Contrainte** : α + β + γ = 1

---

## 4. VARIABLES DE DÉCISION

### 4.1 Variables Binaires de Localisation
- **y_j ∈ {0, 1}** ∀j ∈ J
  - y_j = 1 si l'hôpital j est ouvert
  - y_j = 0 sinon

### 4.2 Variables Binaires d'Affectation (Patients Urgents)
- **x_ij^u ∈ {0, 1}** ∀i ∈ I, ∀j ∈ J
  - x_ij^u = 1 si les patients urgents de la ville i sont affectés à l'hôpital j
  - x_ij^u = 0 sinon

### 4.3 Variables Binaires d'Affectation (Patients Normaux)
- **x_ij^n ∈ {0, 1}** ∀i ∈ I, ∀j ∈ J
  - x_ij^n = 1 si les patients normaux de la ville i sont affectés à l'hôpital j
  - x_ij^n = 0 sinon

### 4.4 Variables Continues de Pénalité
- **p_i ≥ 0** ∀i ∈ I
  - p_i : Pénalité de distance excessive pour la ville i

---

## 5. FONCTION OBJECTIF

### 5.1 Objectif Global Multi-critères

```
MIN Z = α × Z_économique - β × Z_qualité + γ × Z_équité
```

### 5.2 Composantes de l'Objectif

#### A) Critère Économique (Z_économique)

```
Z_économique = Z_fixe + Z_exploitation + Z_transport_u + Z_transport_n
```

Où :

**Coûts fixes** :
```
Z_fixe = ∑(j∈J) f_j × y_j
```

**Coûts d'exploitation** :
```
Z_exploitation = ∑(j∈J) o_j × y_j
```

**Coûts de transport urgents** :
```
Z_transport_u = ∑(i∈I) ∑(j∈J) w_i^u × d_ij × c_u × x_ij^u
```

**Coûts de transport normaux** :
```
Z_transport_n = ∑(i∈I) ∑(j∈J) w_i^n × d_ij × c_n × x_ij^n
```

#### B) Critère Qualité (Z_qualité) - À MAXIMISER

```
Z_qualité = ∑(i∈I) ∑(j∈J) q_j × (x_ij^u + x_ij^n) × w_i
```

Note : Signe négatif dans l'objectif global car on maximise la qualité.

#### C) Critère Équité (Z_équité) - Pénalités

```
Z_équité = K × ∑(i∈I) p_i
```

Où K = 1000 est un coefficient de normalisation.

---

## 6. CONTRAINTES

### 6.1 Contraintes d'Affectation

**C1 - Affectation unique des patients urgents** :
```
∑(j∈J) x_ij^u = 1     ∀i ∈ I
```
Chaque ville affecte ses patients urgents à exactement un hôpital.

**C2 - Affectation unique des patients normaux** :
```
∑(j∈J) x_ij^n = 1     ∀i ∈ I
```
Chaque ville affecte ses patients normaux à exactement un hôpital.

### 6.2 Contraintes de Capacité

**C3 - Capacité pour patients urgents** :
```
∑(i∈I) w_i^u × x_ij^u ≤ cap_j^u × y_j     ∀j ∈ J
```
La demande urgente affectée à un hôpital ne peut excéder sa capacité urgente, et seulement si l'hôpital est ouvert.

**C4 - Capacité pour patients normaux** :
```
∑(i∈I) w_i^n × x_ij^n ≤ cap_j^n × y_j     ∀j ∈ J
```
La demande normale affectée à un hôpital ne peut excéder sa capacité normale, et seulement si l'hôpital est ouvert.

### 6.3 Contraintes de Distance Maximale (Service)

**C5 - Distance maximale pour patients urgents** :
```
d_ij × x_ij^u ≤ D_max^u     ∀i ∈ I, ∀j ∈ J
```
Les patients urgents ne peuvent être affectés qu'à des hôpitaux situés dans un rayon maximal.

**C6 - Distance maximale pour patients normaux** :
```
d_ij × x_ij^n ≤ D_max^n     ∀i ∈ I, ∀j ∈ J
```
Les patients normaux ne peuvent être affectés qu'à des hôpitaux dans un rayon maximal (plus large que pour urgents).

### 6.4 Contrainte Budgétaire

**C7 - Budget total** :
```
∑(j∈J) f_j × y_j ≤ B
```
Le total des coûts fixes d'ouverture ne peut dépasser le budget disponible.

### 6.5 Contraintes de Lien Logique

**C8 - Lien affectation-ouverture (urgents)** :
```
x_ij^u ≤ y_j     ∀i ∈ I, ∀j ∈ J
```
On ne peut affecter des patients à un hôpital que s'il est ouvert.

**C9 - Lien affectation-ouverture (normaux)** :
```
x_ij^n ≤ y_j     ∀i ∈ I, ∀j ∈ J
```

### 6.6 Contraintes de Pénalité (Équité)

**C10 - Calcul des pénalités de distance** :
```
p_i ≥ d_ij - 0.8 × D_max^u     ∀i ∈ I, ∀j ∈ J
```
Pénalise les affectations qui approchent ou dépassent 80% de la distance maximale.

### 6.7 Contrainte de Qualité Minimale

**C11 - Au moins un hôpital de haute qualité** :
```
∑(j∈J : spec_j ≥ 2) y_j ≥ 1
```
Garantit qu'au moins un hôpital de spécialisation avancée (≥2) soit ouvert.

### 6.8 Contraintes de Domaine

```
y_j ∈ {0, 1}                    ∀j ∈ J
x_ij^u ∈ {0, 1}                 ∀i ∈ I, ∀j ∈ J
x_ij^n ∈ {0, 1}                 ∀i ∈ I, ∀j ∈ J
p_i ≥ 0                         ∀i ∈ I
```

---

## 7. COMPLEXITÉ DU MODÈLE

### 7.1 Nombre de Variables
- **Variables binaires de localisation** : m
- **Variables binaires d'affectation urgents** : n × m
- **Variables binaires d'affectation normaux** : n × m
- **Variables continues de pénalité** : n

**Total variables** : m + 2nm + n = m(1 + 2n) + n

Pour n=15 villes et m=7 sites : **7 + 2×15×7 + 15 = 232 variables**
(dont 217 binaires, 15 continues)

### 7.2 Nombre de Contraintes
- Affectation unique urgents : n
- Affectation unique normaux : n
- Capacité urgents : m
- Capacité normaux : m
- Distance max urgents : n × m
- Distance max normaux : n × m
- Budget : 1
- Lien logique urgents : n × m
- Lien logique normaux : n × m
- Pénalités : n × m
- Qualité minimale : 1

**Total contraintes** : 2n + 2m + 5nm + 2 = 5nm + 2n + 2m + 2

Pour n=15, m=7 : **5×15×7 + 2×15 + 2×7 + 2 = 569 contraintes**

### 7.3 Classification
- **Type** : Programmation Linéaire Mixte en Nombres Entiers (PLNE/MILP)
- **Classe de complexité** : NP-difficile
- **Sous-classe** : Problème de localisation capacitée (Capacitated Facility Location Problem - CFLP)
- **Extensions** : Multi-produits (urgents/normaux), multi-critères, contraintes de service

---

## 8. ENRICHISSEMENTS ET VARIANTES

### 8.1 Enrichissements Implémentés
1. ✅ **Séparation urgents/normaux** : Deux types de patients avec capacités séparées
2. ✅ **Multi-critères** : Optimisation simultanée coût/qualité/équité
3. ✅ **Spécialisations** : Niveaux de service différenciés
4. ✅ **Contraintes de distance** : Garanties de qualité de service
5. ✅ **Contrainte budgétaire** : Ressources limitées
6. ✅ **Pénalités d'équité** : Favorise l'accessibilité géographique
7. ✅ **Qualité minimale** : Au moins un hôpital performant
8. ✅ **Coûts d'exploitation** : Coûts récurrents en plus des coûts fixes
9. ✅ **Coûts de transport différenciés** : Urgents plus coûteux
10. ✅ **10 paramètres complexes** : Nombre très élevé de paramètres

### 8.2 Extensions Possibles (Niveau Expert)
1. **Fenêtres temporelles** : Horaires d'ouverture des hôpitaux
2. **Plusieurs périodes** : Planification dynamique
3. **Incertitude** : Demande stochastique
4. **Robustesse** : Solutions résistantes aux variations
5. **Extensions de capacité** : Possibilité d'agrandir certains hôpitaux
6. **Personnels médicaux** : Contraintes de staffing
7. **Matériel médical** : Équipements spécialisés
8. **Flotte d'ambulances** : Véhicules de transport
9. **Hiérarchie de soins** : Référencements entre hôpitaux
10. **Objectifs de couverture** : Pourcentage minimal de population couverte

---

## 9. MÉTHODES DE RÉSOLUTION

### 9.1 Méthode Utilisée : Branch-and-Cut (Gurobi)
L'algorithme de Gurobi combine :
- **Branch-and-Bound** : Exploration intelligente de l'arbre de décision
- **Cutting Planes** : Renforcement de la relaxation linéaire
- **Heuristiques** : Solutions initiales et recherche locale
- **Présolve** : Simplification du modèle

### 9.2 Paramètres de Qualité
- **MIPGap** : Tolérance d'optimalité (défaut : 1%)
  - Gap = |(Best Bound - Best Solution)| / |Best Solution|
- **TimeLimit** : Temps maximal de calcul (défaut : 60s)

### 9.3 Garanties de Solution
- Si MIPGap = 0% : **Solution prouvée optimale**
- Si MIPGap ≤ 1% : **Solution quasi-optimale** (< 1% de l'optimal)
- Si TimeLimit atteint : **Meilleure solution trouvée** (peut être sous-optimale)

---

## 10. INTERPRÉTATION DES RÉSULTATS

### 10.1 Variables de Sortie
- **Objectif Z*** : Valeur optimale de la fonction multi-critères
- **y_j*** : Sites sélectionnés pour ouverture
- **x_ij^u***, **x_ij^n*** : Affectations optimales

### 10.2 Indicateurs de Performance
1. **Économiques**
   - Coût total
   - Coût par patient
   - Répartition des coûts (fixes/exploitation/transport)

2. **Opérationnels**
   - Nombre d'hôpitaux ouverts
   - Taux d'utilisation des capacités (urgents/normaux)
   - Distance moyenne de transport
   - Distance maximale réelle

3. **Qualité**
   - Qualité moyenne de service
   - Niveau de spécialisation moyen
   - Couverture géographique

4. **Computationnels**
   - Temps de calcul
   - Gap MIP final
   - Nombre de nœuds explorés (Branch-and-Bound)

### 10.3 Analyse de Sensibilité
Impact de la variation de :
- **Budget** : Combien d'hôpitaux supplémentaires avec +X% de budget?
- **Capacités** : Effet de l'augmentation des capacités
- **Coûts de transport** : Sensibilité aux coûts logistiques
- **Distances maximales** : Impact des contraintes de service
- **Pondérations α, β, γ** : Compromis coût/qualité/équité

---

## 11. RÉFÉRENCES THÉORIQUES

### 11.1 Problèmes Classiques Liés
1. **Facility Location Problem (FLP)** : Problème de base
2. **Capacitated FLP (CFLP)** : Avec contraintes de capacité
3. **Multi-commodity FLP** : Plusieurs types de flux (urgents/normaux)
4. **Multi-criteria FLP** : Optimisation multi-objectifs

### 11.2 Littérature
- Cornuéjols et al. (1990) : "A comparison of heuristics and relaxations for the capacitated plant location problem"
- Daskin (1995) : "Network and Discrete Location"
- Current et al. (2002) : "The covering salesman problem"
- Farahani et al. (2012) : "Competitive facility location problems: A survey"

### 11.3 Applications Réelles
- Planification de réseaux hospitaliers
- Localisation de centres de secours (pompiers, SAMU)
- Distribution de services d'urgence
- Planification de centres de vaccination
- Logistique humanitaire

---

## 12. VALIDATION ET TESTS

### 12.1 Tests de Validité
✅ **Faisabilité** : 
- Vérifier que ∑ cap_j^u ≥ ∑ w_i^u
- Vérifier que ∑ cap_j^n ≥ ∑ w_i^n

✅ **Cohérence** :
- Toutes les villes sont affectées
- Pas de dépassement de capacité
- Budget respecté
- Distances maximales respectées

✅ **Optimalité** :
- Gap MIP < seuil
- Comparaison avec bornes théoriques

### 12.2 Jeux de Test
- **Petites instances** : n=5, m=3 (résolution rapide)
- **Moyennes instances** : n=15, m=7 (standard)
- **Grandes instances** : n=50, m=20 (challenge)

---

**Document rédigé pour le projet de Recherche Opérationnelle**  
**INSAT - Institut National des Sciences Appliquées et de Technologie**  
**Date : Décembre 2025**
