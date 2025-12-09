# Facility Location & Allocation Optimization App

This document explains the problem being solved, the modeling approach (PL / PLNE / PLM), the application architecture, and how to use the GUI.

---

# 1. Problem Description

The application solves a **Facility Location and Allocation** optimization problem. The goal is to:

* Decide **where to open facilities** (distribution centers).
* Decide **which customers are served by which facility**.
* Optionally consider capacities, demands, fixed costs, and transport costs.
* Minimize the **total operational cost**.

This type of problem appears in logistics, supply chain design, delivery planning, and warehouse placement.

The model supports:

* **PL (Linear Programming)** — all decision variables continuous.
* **PLNE (Integer Linear Programming)** — binary facility-opening variables, continuous allocation.
* **PLM (Mixed Integer Programming)** — mix of integer and continuous variables.

---

# 2. Mathematical Model

## Decision Variables

* **y_j**: Binary (or continuous, depending on model type). Indicates if facility *j* is opened.
* **x_ij**: Allocation from facility *j* to customer *i*.

## Objective Function

Minimize

```
Total Cost = sum_j (FixedCost_j * y_j)
           + sum_i sum_j (TransportCost_ij * x_ij)
```

Transport cost = distance × transport_cost_per_unit.

## Constraints

1. **Demand satisfaction:**

```
For each customer i:
    sum_j x_ij = demand_i
```

2. **Facility capacity:**

```
For each facility j:
    sum_i x_ij <= capacity_j * y_j
```

3. **Non-negativity:**

```
x_ij >= 0
```

4. **Binary facility choice (for PLNE/PLM):**

```
y_j ∈ {0,1}
```

---

# 3. Application Architecture (Python)

## Technologies Used

* **Python**
* **PySide6 (Qt)** for GUI
* **Gurobi** for optimization
* **Matplotlib** for solution visualization
* **Multithreading (QThread)** to keep UI responsive during solving

## Major Components

### 1. Data Entry (GUI Tab)

* Uses `QTableWidget` to enter:

  * Facility data (capacity, fixed cost, coordinates)
  * Customer data (demand, coordinates)
* Buttons for loading/saving datasets (JSON).

### 2. Solver (GUI Tab)

* Select model type (PL / PLNE / PLM).
* Adjust parameters (transport cost, time limits).
* Launch solving in a separate worker thread.
* Results displayed after optimization:

  * Optimal objective
  * List of opened facilities
  * Allocation table

### 3. Visualization (GUI Tab)

* Scatter plot of facilities and customers
* Lines showing allocation
* Colors and markers for clarity

---

# 4. How to Use the Application

1. **Enter Data**

   * Go to the Data tab.
   * Enter facility and customer information into the tables.

2. **Choose Model Type**

   * PL → continuous
   * PLNE → binary facility opening
   * PLM → mixed

3. **Solve**

   * Click "Solve".
   * The progress bar indicates background thread progress.

4. **Inspect Results**

   * Read objective value.
   * See which facilities opened.
   * See allocations.

5. **Visualize**

   * Open the Visualization tab and press "Plot Solution".

---

# 5. Dataset Format (JSON)

Example:

```json
{
    "facilities": [
        {"capacity": 100, "fixed_cost": 500, "x": 10, "y": 20},
        {"capacity": 80, "fixed_cost": 400, "x": 30, "y": 40}
    ],
    "customers": [
        {"demand": 50, "x": 15, "y": 25},
        {"demand": 30, "x": 35, "y": 45}
    ]
}
```

---

# 6. Extending the Project

To improve evaluation, you can add:

* Time windows for customers
* Multiple capacity types (weight & volume)
* Multi-objective optimization
* Maximum number of facilities allowed
* Additional business constraints

I can integrate any of these — just tell me.

---

# 7. Requirements

```
Python 3.x
PySide6
matplotlib
gurobipy (Gurobi 10)
```

---

# 8. Running the Application

```
python facility_allocation_app.py
```

---

# 9. Authors & Documentation

This README documents:

* Problem definition
* Mathematical model
* GUI architecture
* Solver behavior
* Data format
* How to run and extend the project
