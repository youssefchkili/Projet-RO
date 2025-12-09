# Projet d'Optimisation de Distribution de Gaz

Ce projet implémente un système d'aide à la décision pour optimiser la distribution de gaz naturel de différentes qualités à travers un réseau de pipelines. Il utilise **Gurobi** pour l'optimisation et **PyQt6** pour l'interface graphique utilisateur.

## Modélisation Mathématique

Nous avons modélisé ce problème comme un **Problème de Flot à Coût Minimum Multi-Flots avec Coûts Fixes** (Multi-Commodity Minimum Cost Network Flow Problem with Fixed Costs). Il s'agit d'un problème de Programmation Linéaire en Nombres Entiers (PLNE / MILP).

### 1. Ensembles et Indices
*   $N$ : Ensemble des nœuds du réseau (Sources, Jonctions, Puits).
*   $A$ : Ensemble des arcs (pipelines) connectant les nœuds $(i, j)$.
*   $K$ : Ensemble des commodités (Qualités/Types de gaz).

### 2. Paramètres
*   $c_{ij}$ : Coût variable de transport par unité de flux sur l'arc $(i,j)$.
*   $f_{ij}$ : Coût fixe opérationnel pour l'utilisation de l'arc $(i,j)$ (ex: maintenance, pressurisation).
*   $u_{ij}$ : Capacité maximale de l'arc $(i,j)$ (partagée par toutes les qualités de gaz).
*   $d_{k,i}$ : Demande nette de la commodité $k$ au nœud $i$.
    *   Si $d_{k,i} > 0$ : Le nœud $i$ est un puits (consommateur) pour la qualité $k$.
    *   Si $d_{k,i} < 0$ : Le nœud $i$ est une source (producteur) pour la qualité $k$.
    *   Si $d_{k,i} = 0$ : Le nœud $i$ est un nœud de transit.

### 3. Variables de Décision
*   **Variables de Flux (Continues)** : $x_{ijk} \ge 0$
    *   Représente la quantité de gaz de qualité $k$ circulant sur l'arc $(i,j)$.
*   **Variables d'Activation (Binaires)** : $y_{ij} \in \{0, 1\}$
    *   Vaut $1$ si l'arc $(i,j)$ est utilisé (actif), $0$ sinon. Cela permet de modéliser les coûts fixes.

### 4. Fonction Objectif
Minimiser le coût total (Coût Variable de Transport + Coût Fixe Opérationnel) :

$$
\text{Minimiser } Z = \underbrace{\sum_{(i,j) \in A} \sum_{k \in K} c_{ij} \cdot x_{ijk}}_{\text{Coût Opérationnel}} + \underbrace{\sum_{(i,j) \in A} f_{ij} \cdot y_{ij}}_{\text{Coût d'Infrastructure}}
$$

### 5. Contraintes

**a) Contraintes de Conservation du Flux (Loi de Kirchhoff) :**
Pour chaque nœud $i \in N$ et chaque commodité $k \in K$ :
$$
\sum_{j:(j,i) \in A} x_{jik} - \sum_{j:(i,j) \in A} x_{ijk} = d_{k,i}
$$
*(Entrée - Sortie = Demande Nette)*

**b) Contraintes de Capacité (Pipeline Partagé) :**
La somme des flux de toutes les qualités de gaz dans un pipeline ne doit pas dépasser sa capacité. De plus, le flux n'est autorisé que si le pipeline est actif ($y_{ij}=1$).
$$
\sum_{k \in K} x_{ijk} \le u_{ij} \cdot y_{ij} \quad \forall (i,j) \in A
$$
*Si $y_{ij}=0$ (pipeline fermé), alors la capacité effective est 0.*

**c) Non-négativité et Intégralité :**
$$
x_{ijk} \ge 0
$$
$$
y_{ij} \in \{0, 1\}
$$

## Installation et Exécution

1.  **Prérequis** :
    *   Python 3.8+
    *   Gurobi Optimizer (Licence requise)
    
2.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Lancer l'application** :
    ```bash
    python src/main.py
    ```

## Fonctionnalités
*   **Saisie de Données** : Interface tabulaire pour définir la topologie du réseau (arcs) et les demandes de gaz (commodités).
*   **Optimisation** : Résout le modèle PLNE en utilisant Gurobi dans un thread d'arrière-plan pour ne pas bloquer l'interface.
*   **Visualisation** : Affiche le flux optimal du réseau graphiquement en utilisant Matplotlib.
