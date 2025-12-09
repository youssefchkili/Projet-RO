# GUIDE D'UTILISATION DÉTAILLÉ
## Application de Localisation d'Hôpitaux - Interface Avancée

---

## 📖 Table des Matières

1. [Démarrage Rapide](#démarrage-rapide)
2. [Génération d'Instance](#génération-dinstance)
3. [Configuration du Solveur](#configuration-du-solveur)
4. [Lancement de l'Optimisation](#lancement-de-loptimisation)
5. [Interprétation des Résultats](#interprétation-des-résultats)
6. [Analyse de Sensibilité](#analyse-de-sensibilité)
7. [Export des Résultats](#export-des-résultats)
8. [Édition Manuelle](#édition-manuelle)
9. [Cas d'Usage](#cas-dusage)
10. [Dépannage](#dépannage)

---

## 1. Démarrage Rapide

### Lancement de l'Application

```powershell
# Naviguer vers le dossier du projet
cd "c:\Users\youss\OneDrive\Desktop\My Work\GL\GL INSAT\Projet RO"

# Lancer l'interface avancée
python gui_app_advanced.py
```

### Première Utilisation (3 étapes)

1. **Onglet "📊 Données"** → Cliquez sur "🎲 Générer Instance"
2. **Onglet "⚙️ Solveur"** → Cliquez sur "🚀 LANCER OPTIMISATION"
3. **Consultez les résultats** dans les différents onglets de visualisation

---

## 2. Génération d'Instance

### 2.1 Génération Automatique

**Localisation** : Onglet "📊 Données" → Section "🎲 Génération automatique"

**Paramètres** :
- **Villes** (5-50) : Nombre de villes à desservir
  - 5-10 : Petit problème (résolution < 10s)
  - 10-20 : Problème moyen (résolution < 60s)
  - 20-50 : Grand problème (peut nécessiter > 5 min)
  
- **Sites** (3-20) : Nombre de sites candidats pour hôpitaux
  - Règle empirique : m ≈ n/2 à n/3
  
- **Seed** (1-9999) : Graine aléatoire pour reproductibilité
  - Même seed → Même instance
  - Utile pour comparer différentes configurations

**Résultat** :
- Génération de tous les paramètres (10 catégories)
- Affichage automatique sur la carte
- Résumé dans l'encadré "📄 Résumé de l'instance"

### 2.2 Import CSV

**Localisation** : Onglet "📊 Données" → "💾 Import/Export" → "📥 Import CSV"

**Format CSV attendu** :
```csv
Type,Paramètre,Valeur
Config,n_customers,15
Config,m_sites,7
Customer,0_x,12.5
Customer,0_y,45.3
...
```

### 2.3 Validation Automatique

L'application vérifie automatiquement :
- ✅ Capacités totales ≥ Demande totale
- ✅ Budget > 0
- ✅ Distances cohérentes
- ❌ Si problème → Message d'erreur

---

## 3. Configuration du Solveur

### 3.1 Paramètres Gurobi

**Localisation** : Onglet "⚙️ Solveur" → "🔧 Paramètres Gurobi"

#### Temps Limite (Time Limit)
- **Plage** : 10 - 600 secondes
- **Défaut** : 60 secondes
- **Recommandations** :
  - 10-30s : Test rapide, solution approximative
  - 60s : Bon compromis qualité/temps
  - 120-300s : Recherche de meilleure solution
  - 600s : Pour grands problèmes complexes

#### MIP Gap
- **Plage** : 0.01% - 10%
- **Défaut** : 1%
- **Signification** : Tolérance d'optimalité
  - Gap = |(Meilleure solution - Borne) / Meilleure solution|
- **Recommandations** :
  - 0.01-0.1% : Solution quasi-optimale (lent)
  - 1% : Excellent compromis (défaut)
  - 5-10% : Solution rapide mais approximative

### 3.2 Pondérations Multi-critères

**Localisation** : Onglet "⚙️ Solveur" → "🎯 Pondération Multi-critères"

#### Contrainte : α + β + γ = 1.0

Les sliders s'ajustent automatiquement pour maintenir cette contrainte.

#### α (Coût Économique)
- **Plage** : 0.0 - 1.0
- **Défaut** : 0.7 (70%)
- **Impact** :
  - ↑ α : Moins d'hôpitaux, coûts minimaux
  - ↓ α : Plus d'hôpitaux, meilleur service

#### β (Qualité de Service)
- **Plage** : 0.0 - 1.0
- **Défaut** : 0.2 (20%)
- **Impact** :
  - ↑ β : Hôpitaux plus spécialisés sélectionnés
  - ↓ β : Ignore la qualité, focus coût

#### γ (Équité Géographique)
- **Plage** : 0.0 - 1.0
- **Défaut** : 0.1 (10%)
- **Impact** :
  - ↑ γ : Couverture plus homogène du territoire
  - ↓ γ: Accepte distances importantes

#### Configurations Prédéfinies

| Scénario | α | β | γ | Résultat Attendu |
|----------|---|---|---|------------------|
| **Budget serré** | 1.0 | 0.0 | 0.0 | Coût minimal absolu |
| **Standard** | 0.7 | 0.2 | 0.1 | Équilibre coût-qualité |
| **Haute qualité** | 0.3 | 0.6 | 0.1 | Hôpitaux d'excellence |
| **Équité rurale** | 0.4 | 0.2 | 0.4 | Accessibilité maximale |

---

## 4. Lancement de l'Optimisation

### 4.1 Pré-requis

- ✅ Instance chargée (génération ou import)
- ✅ Bouton "🚀 LANCER OPTIMISATION" actif

### 4.2 Processus d'Optimisation

**Cliquez sur "🚀 LANCER OPTIMISATION"**

#### Phase 1 : Initialisation (< 1s)
- Construction du modèle Gurobi
- Création des variables et contraintes
- Affichage : "🔄 Démarrage du solveur Gurobi..."

#### Phase 2 : Présolve (1-5s)
- Simplification du modèle
- Élimination de variables redondantes
- Renforcement de contraintes

#### Phase 3 : Optimisation (variable)
- Exploration Branch-and-Bound
- Génération de coupes (cutting planes)
- Amélioration progressive de la solution

**Indicateurs Temps Réel** :
- **Meilleure solution** : Objectif de la meilleure solution entière trouvée
- **Borne inférieure** : Limite théorique (relaxation LP)
- **Gap** : Écart relatif = |(Best - Bound) / Best|

#### Phase 4 : Finalisation (< 1s)
- Extraction de la solution
- Calcul des statistiques
- Affichage des résultats

### 4.3 Critères d'Arrêt

L'optimisation s'arrête si :
1. ✅ **Solution optimale prouvée** (gap = 0%)
2. ⏱️ **Temps limite atteint** (solution sous-optimale retournée)
3. 📊 **Gap cible atteint** (MIP Gap)
4. 🔴 **Problème infaisable** (aucune solution)

### 4.4 Pendant l'Optimisation

**Interface Non-Bloquante** :
- ✅ Peut consulter le journal
- ✅ Peut changer d'onglet
- ❌ Ne peut pas relancer une nouvelle optimisation

---

## 5. Interprétation des Résultats

### 5.1 Journal d'Exécution

**Localisation** : Bas du panneau gauche

**Messages Clés** :
```
✅ Solution optimale trouvée!
📊 Objectif: 87652.34
🏥 Hôpitaux ouverts: 4/7
⏱️ Temps: 3.42s
```

### 5.2 Onglet "🗺️ Carte"

**Visualisation Géographique** :

**Éléments** :
- 🔵 **Cercles bleus** : Villes (taille proportionnelle à la population)
- 🟢 **Carrés verts** : Hôpitaux ouverts (bordure épaisse)
- 🔴 **Carrés gris** : Sites fermés (transparents)
- 🔴 **Lignes rouges** : Affectation patients urgents (épaisses)
- 🔵 **Lignes bleues pointillées** : Affectation patients normaux (fines)

**Annotations** :
- Villes : "V0", "V1", ... avec nombre de patients
- Hôpitaux ouverts : "H2★" (étoile = ouvert) avec spécialisation

**Interprétation** :
- ✅ **Lignes courtes** : Bonne accessibilité
- ❌ **Lignes longues** : Possible amélioration
- 🎯 **Concentration de lignes** : Hôpital très sollicité

### 5.3 Onglet "📊 Statistiques"

**4 Graphiques** :

#### A) Utilisation des Capacités
- **Histogramme** : Urgents (rouge) vs Normaux (bleu)
- **Objectif** : Idéalement 70-90%
- ⚠️ Si < 50% : Surcapacité, possibilité de réduire
- ⚠️ Si > 95% : Saturation, risque de congestion

#### B) Distances de Transport
- **Histogramme** : Moyenne / Max réel / Limite urgents
- **Interprétation** :
  - Moyenne < Limite/2 : ✅ Excellent
  - Max ≈ Limite : ⚠️ Contrainte active
  - Max > Limite : ❌ Erreur (ne devrait pas arriver)

#### C) Répartition des Sites
- **Camembert** : Ouverts (vert) / Fermés (gris)
- **Ratio typique** : 40-60% de sites ouverts

#### D) Qualité des Hôpitaux Ouverts
- **Barres horizontales** : Qualité par hôpital
- **Couleur** : Vert (haute qualité) → Rouge (basse)
- **Objectif** : Maximiser nombre de barres vertes

### 5.4 Onglet "💰 Coûts"

**2 Graphiques** :

#### A) Camembert de Répartition
- 🔴 **Coûts fixes** : Ouverture des hôpitaux
- 🔵 **Exploitation** : Fonctionnement annuel
- 🔴 **Transport urgents** : Ambulances
- 🔵 **Transport normaux** : Véhicules standards

**Répartitions Typiques** :
- Budget serré : Fixes 60%, Transport 30%, Exploitation 10%
- Équilibré : Fixes 40%, Transport 40%, Exploitation 20%
- Haute qualité : Fixes 50%, Transport 35%, Exploitation 15%

#### B) Histogramme Détaillé
- **Valeurs absolues** en €
- **Annotations** : Montant exact sur chaque barre

**Leviers d'Action** :
- ↓ Coûts fixes : Ouvrir moins d'hôpitaux
- ↓ Transport : Ouvrir plus d'hôpitaux proches
- ↓ Exploitation : Sélectionner sites moins coûteux

### 5.5 Métriques Détaillées

**Dans le Journal** :

```
Détail des coûts:
  - Coûts fixes: 35000.00 €
  - Coûts d'exploitation: 7000.00 €
  - Transport urgents: 28456.12 €
  - Transport normaux: 17196.22 €
  - Total coûts: 87652.34 €

Indicateurs de performance:
  - Qualité moyenne: 65.23
  - Distance moyenne: 15.67 km
  - Distance max: 28.91 km
  - Taux utilisation urgents: 78.3%
  - Taux utilisation normaux: 81.5%
  - Gap MIP: 0.45%
  - Temps de calcul: 3.42s
```

**Benchmarks** :

| Métrique | Mauvais | Acceptable | Excellent |
|----------|---------|------------|-----------|
| Gap MIP | > 5% | 1-5% | < 1% |
| Taux capacité | < 50% ou > 95% | 60-80% | 70-85% |
| Distance moy. | > 30 km | 15-30 km | < 15 km |
| Qualité moy. | < 40 | 40-70 | > 70 |

---

## 6. Analyse de Sensibilité

### 6.1 Objectif

**Répondre aux questions** :
- Comment varie la solution si le budget augmente de 20%?
- Quel impact d'une augmentation des capacités?
- La solution est-elle sensible aux coûts de transport?

### 6.2 Procédure

**Localisation** : Onglet "📈 Sensibilité"

**Étapes** :
1. **Sélectionner paramètre** :
   - Budget maximal
   - Capacités hôpitaux
   - Coûts de transport
   - Distance maximale urgents

2. **Définir variation** :
   - Exemple : ±50% = analyse de 50% à 150% de la valeur nominale
   
3. **Nombre de points** :
   - 3 points : Rapide, vue d'ensemble
   - 5 points : Standard, bon compromis
   - 10 points : Détaillé, courbe lisse (plus long)

4. **Lancer** : Cliquez sur "📊 Lancer Analyse de Sensibilité"

5. **Patienter** : Chaque point = 1 optimisation complète
   - 5 points × 30s = ~2.5 min

### 6.3 Interprétation

**Onglet "📈 Sensibilité"** affiche 2 graphiques :

#### Graphique 1 : Impact sur l'Objectif
- **Axe X** : Facteur multiplicatif (1.0 = valeur nominale)
- **Axe Y** : Valeur de l'objectif (€)
- **Ligne verticale rouge** : Valeur actuelle

**Interprétations** :
- 📉 **Décroissante** : Augmenter ce paramètre réduit le coût
  - Exemple : Budget ↑ → Objectif ↓ (plus d'options)
- 📈 **Croissante** : Augmenter ce paramètre augmente le coût
  - Exemple : Coûts transport ↑ → Objectif ↑ (impact direct)
- ➡️ **Plate** : Paramètre peu influent
  - Exemple : Capacités déjà suffisantes

#### Graphique 2 : Impact sur Nombre d'Hôpitaux
- **Relation** : Objectif vs Nombre de sites ouverts
- **Interprétations** :
  - Croissant : Plus de budget → Plus d'hôpitaux
  - Constant : Contrainte autre (capacité, distance) limite
  - Par paliers : Seuils discrets (nature binaire du problème)

### 6.4 Cas d'Usage

**Scénario 1 : Négociation Budgétaire**
- Variation : Budget ±30%
- Question : Combien économiser avec 10% de budget en moins?
- Utilisation : Argumenter auprès des décideurs

**Scénario 2 : Extension de Capacités**
- Variation : Capacités +50%
- Question : Vaut-il la peine d'agrandir les hôpitaux?
- Utilisation : Planification à moyen terme

**Scénario 3 : Évolution des Coûts**
- Variation : Coûts transport ±40%
- Question : Sensibilité à l'inflation du carburant?
- Utilisation : Analyse de risque

---

## 7. Export des Résultats

### 7.1 Export PDF

**Bouton** : "📄 Export PDF"

**Contenu** :
- Page 1 : Carte géographique de la solution
- Page 2 : Statistiques (4 graphiques)
- Page 3 : Analyse des coûts (2 graphiques)
- Page 4 : Sensibilité (si effectuée)

**Format** : Multi-pages, haute résolution (300 DPI)

**Usage** :
- ✅ Rapport pour présentation
- ✅ Documentation du projet
- ✅ Impression pour réunion

### 7.2 Export JSON

**Bouton** : "📋 Export JSON"

**Structure** :
```json
{
  "timestamp": "2025-12-03T14:30:00",
  "instance": {
    "n_customers": 15,
    "m_sites": 7,
    "budget_max": 45000.0
  },
  "results": {
    "objective": 87652.34,
    "n_opened": 4,
    "opened_sites": [1, 3, 5, 6],
    "fixed_cost": 35000.0,
    ...
  }
}
```

**Usage** :
- ✅ Analyse externe (Python, R, Excel)
- ✅ Archivage structuré
- ✅ Intégration dans autre système

### 7.3 Export CSV Résultats

**Bouton** : "📊 Export Résultats CSV"

**Sections** :
1. **En-tête** : Date, titre
2. **Paramètres instance** : n, m, budget, etc.
3. **Résultats globaux** : Objectif, coûts, qualité, etc.
4. **Affectations détaillées** : Chaque ville → hôpital

**Format** :
```csv
RÉSULTATS OPTIMISATION - LOCALISATION HÔPITAUX
Date,2025-12-03 14:30:00

PARAMÈTRES INSTANCE
Nombre de villes,15
Nombre de sites,7
...

AFFECTATIONS
Ville,Type,Hôpital,Distance (km),Patients
V0,Urgents,H3,12.45,8
V0,Normaux,H3,12.45,25
...
```

**Usage** :
- ✅ Analyse Excel/LibreOffice
- ✅ Tableau de bord
- ✅ Rapport détaillé

### 7.4 Export CSV Données

**Bouton** : "📤 Export CSV" (Onglet Données)

**Contenu** : Paramètres de l'instance uniquement

**Usage** :
- ✅ Sauvegarde de l'instance
- ✅ Partage avec collègues
- ✅ Réimport ultérieur

---

## 8. Édition Manuelle

### 8.1 Accès

**Localisation** : Onglet "📊 Données" → "✏️ Édition manuelle" → "🔧 Modifier les données"

**Conditions** : Instance déjà chargée (génération ou import)

### 8.2 Dialogue d'Édition

**3 Onglets** :

#### Onglet "Villes"
- **Tableau 4 colonnes** :
  - X (km) : Coordonnée longitude
  - Y (km) : Coordonnée latitude
  - Patients Urgents : Nombre
  - Patients Normaux : Nombre

#### Onglet "Sites"
- **Tableau 7 colonnes** :
  - X (km), Y (km) : Coordonnées
  - Coût Fixe : Coût d'ouverture (€)
  - Cap. Urgents : Capacité maximale urgents
  - Cap. Normaux : Capacité maximale normaux
  - Spécialisation : Niveau 0-3
  - Qualité : Score de qualité

#### Onglet "Paramètres"
- **Formulaire** :
  - Budget maximal (€)
  - Distance max urgents (km)
  - Distance max normaux (km)
  - Coût transport urgents (€/km/patient)
  - Coût transport normaux (€/km/patient)

### 8.3 Validation

**Au clic sur "OK"** :
- ✅ Vérification cohérence (capacités ≥ demande)
- ✅ Recalcul automatique des distances
- ✅ Mise à jour affichage

**Si erreur** :
- ❌ Message d'erreur explicite
- ↩️ Retour à l'édition

### 8.4 Cas d'Usage

**Scénario 1 : Ajuster Budget**
- Modifier budget dans "Paramètres"
- Relancer optimisation
- Comparer avec version précédente

**Scénario 2 : Tester Nouvelle Ville**
- Ajouter ligne dans tableau "Villes"
- Renseigner coordonnées et population
- Optimiser

**Scénario 3 : Fermer Site Candidat**
- Mettre coût fixe très élevé dans "Sites"
- Ou mettre capacités à 0
- Site ne sera pas sélectionné

---

## 9. Cas d'Usage

### 9.1 Planification Réseau Hospitalier Régional

**Contexte** :
Une région doit implanter 3-5 nouveaux hôpitaux parmi 10 sites candidats pour desservir 20 villes.

**Workflow** :
1. **Import** : CSV avec coordonnées réelles des villes et sites
2. **Paramétrage** :
   - Budget : Enveloppe régionale
   - Capacités : Selon taille des sites
   - Distances max : Normes d'accessibilité (30 min urgences)
3. **Optimisation** : α=0.6, β=0.3, γ=0.1 (qualité importante)
4. **Analyse** : Vérifier couverture, coûts, accessibilité
5. **Sensibilité** : Impact de ±20% budget
6. **Export** : Rapport PDF pour présentation au conseil régional

### 9.2 Réorganisation Réseau Existant

**Contexte** :
10 hôpitaux actuels, étudier fermetures/redéploiements.

**Workflow** :
1. **Génération** : Instance représentant situation actuelle
2. **Optimisation** : Comparer avec solution optimale
3. **Écart** : Identifier hôpitaux sous-optimaux
4. **Scénarios** :
   - Scénario A : Fermer 2 hôpitaux peu utilisés
   - Scénario B : Agrandir 3 hôpitaux stratégiques
5. **Recommandation** : Exporter comparatif

### 9.3 Planification d'Urgence (Épidémie)

**Contexte** :
Augmentation soudaine de 50% des patients urgents.

**Workflow** :
1. **Instance de base** : Situation normale
2. **Édition** : Multiplier "Patients Urgents" par 1.5
3. **Optimisation** : Vérifier si réseau suffisant
4. **Si insuffisant** :
   - Augmenter capacités urgentes
   - Ou ouvrir sites supplémentaires
5. **Plan de contingence** : Export CSV des recommandations

### 9.4 Étude Comparative Multi-scénarios

**Contexte** :
Comparer 3 stratégies : coût minimal, qualité maximale, équité.

**Workflow** :
1. **Instance unique** : Générer une fois
2. **Scénario 1** : α=1.0, β=0, γ=0 → Optimiser
3. **Scénario 2** : α=0.3, β=0.7, γ=0 → Optimiser
4. **Scénario 3** : α=0.4, β=0.2, γ=0.4 → Optimiser
5. **Comparaison** : Tableau Excel avec exports CSV
6. **Décision** : Choix basé sur priorités politiques

---

## 10. Dépannage

### 10.1 Problèmes Courants

#### ❌ "License expired" ou "No license"

**Causes** :
- Licence Gurobi expirée ou non activée

**Solutions** :
```powershell
# Vérifier licence
gurobi_cl --version

# Réactiver
grbgetkey VOTRE-CLE-ACADEMIQUE

# Si problème persiste, réinstaller
pip uninstall gurobipy
pip install gurobipy
```

#### ❌ "Interface ne se lance pas"

**Causes** :
- PySide6 non installé ou corrompu

**Solutions** :
```powershell
# Réinstaller PySide6
pip uninstall PySide6
pip install PySide6

# Vérifier installation
python -c "from PySide6 import QtWidgets; print('OK')"
```

#### ❌ "Optimisation très lente" (> 10 min)

**Causes** :
- Instance trop grande
- Paramètres trop stricts

**Solutions** :
1. ↑ Augmenter MIP Gap à 5%
2. ↓ Réduire Time Limit à 120s
3. ↓ Réduire taille instance (moins de villes/sites)
4. Vérifier que OutputFlag=0 dans solve_instance()

#### ❌ "Problème infaisable" (pas de solution)

**Causes** :
- Capacités insuffisantes
- Budget trop faible
- Distances maximales trop strictes

**Solutions** :
1. **Vérifier capacités** :
   ```
   Capacité totale urgents ≥ Demande urgents totale
   Capacité totale normaux ≥ Demande normaux totale
   ```
2. **Augmenter budget** : Édition manuelle ou régénération
3. **Assouplir distances** : Augmenter max_distance_urgent/normal

#### ❌ Graphiques ne s'affichent pas

**Causes** :
- Matplotlib non installé
- Erreur dans les données

**Solutions** :
```powershell
pip install matplotlib
```

#### ⚠️ Résultats incohérents

**Causes** :
- Données d'instance corrompues
- Bug dans le modèle

**Solutions** :
1. Régénérer instance avec nouveau seed
2. Vérifier journal pour messages d'erreur
3. Exporter JSON et vérifier manuellement
4. Relancer tests : `python test_advanced.py`

### 10.2 Vérification de l'Installation

**Test complet** :
```powershell
# Test 1 : Dépendances
python -c "import numpy; import matplotlib; from PySide6 import QtWidgets; import gurobipy; print('✅ Toutes dépendances OK')"

# Test 2 : Modèle seul
python solve_facility.py

# Test 3 : Tests unitaires
python test_advanced.py

# Test 4 : Interface
python gui_app_advanced.py
```

**Si tous tests passent** : ✅ Installation parfaite !

### 10.3 Support

**Ressources** :
- Documentation Gurobi : https://www.gurobi.com/documentation/
- Forum PySide : https://forum.qt.io/category/15/pyside
- Stack Overflow : Tag `gurobi` ou `pyside6`

---

## 📚 Annexes

### A.1 Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| Ctrl + G | Générer nouvelle instance |
| Ctrl + O | Optimiser |
| Ctrl + S | Exporter CSV |
| F5 | Rafraîchir affichage |

### A.2 Astuces

💡 **Astuce 1** : Utilisez toujours le même seed pour comparer différentes configurations

💡 **Astuce 2** : Commencez par petit problème (5x3) pour tester rapidement

💡 **Astuce 3** : Gap de 2-5% suffit souvent, inutile de chercher 0.01%

💡 **Astuce 4** : Consultez onglet Sensibilité pour insights stratégiques

💡 **Astuce 5** : Exportez JSON pour analyses avancées en Python/R

### A.3 Exemples de Résultats

**Instance 15x7, Seed 42, α=0.7, β=0.2, γ=0.1** :
- Objectif : 87,652 €
- Hôpitaux : 4 ouverts (sites 1, 3, 5, 6)
- Distance moyenne : 15.7 km
- Capacité urgents : 78%
- Temps : 3.4s
- Gap : 0.45%

**Instance 20x10, Seed 123, α=0.5, β=0.4, γ=0.1** :
- Objectif : 145,234 €
- Hôpitaux : 6 ouverts
- Distance moyenne : 12.3 km
- Capacité urgents : 85%
- Temps : 18.7s
- Gap : 1.2%

---

**Document rédigé pour le projet de Recherche Opérationnelle**  
**INSAT - Institut National des Sciences Appliquées et de Technologie**  
**Version 2.0 - Décembre 2025**
