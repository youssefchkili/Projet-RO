import sys
import json
import math
import traceback
from dataclasses import dataclass, asdict
from typing import List, Tuple

from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QComboBox, QSpinBox, QDoubleSpinBox, QProgressBar, QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Gurobi
try:
    from gurobipy import Model, GRB
    GUROBI_AVAILABLE = True
except Exception as e:
    GUROBI_AVAILABLE = False

@dataclass
class Facility:
    id: int
    x: float = 0.0
    y: float = 0.0
    fixed_cost: float = 100.0
    capacity: float = 100.0

@dataclass
class Customer:
    id: int
    x: float = 0.0
    y: float = 0.0
    demand: float = 10.0

@dataclass
class ProblemData:
    facilities: List[Facility]
    customers: List[Customer]
    transportation_cost_per_distance: float = 1.0
    model_type: str = 'PLNE'

def euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0]-b[0], a[1]-b[1])


class SolverThread(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, data: ProblemData):
        super().__init__()
        self.data = data

    def run(self):
        try:
            if not GUROBI_AVAILABLE:
                raise RuntimeError("Gurobi python package (gurobipy) not available.")

            fac = self.data.facilities
            cust = self.data.customers
            m = Model("FacilityLocation")
            m.setParam('OutputFlag', 0)

            y = {}
            x = {}

            is_integer = (self.data.model_type.upper() == 'PLNE')

            for j in range(len(fac)):
                if is_integer:
                    y[j] = m.addVar(vtype=GRB.BINARY, name=f"y_{j}")
                else:
                    y[j] = m.addVar(lb=0.0, ub=1.0, name=f"y_{j}")

            for i in range(len(cust)):
                for j in range(len(fac)):
                    x[i,j] = m.addVar(lb=0.0, name=f"x_{i}_{j}")

            m.update()

            fixed_cost_expr = sum(fac[j].fixed_cost * y[j] for j in range(len(fac)))

            dist = {}
            for i in range(len(cust)):
                for j in range(len(fac)):
                    d = euclidean((cust[i].x, cust[i].y), (fac[j].x, fac[j].y))
                    dist[i,j] = d

            transport_cost_expr = sum(self.data.transportation_cost_per_distance * dist[i,j] * x[i,j]
                                       for i in range(len(cust)) for j in range(len(fac)))

            m.setObjective(fixed_cost_expr + transport_cost_expr, sense=GRB.MINIMIZE)

            for i in range(len(cust)):
                m.addConstr(sum(x[i,j] for j in range(len(fac))) == cust[i].demand,
                            name=f"demand_{i}")

            for j in range(len(fac)):
                m.addConstr(sum(x[i,j] for i in range(len(cust))) <= fac[j].capacity * y[j],
                            name=f"cap_{j}")

            if not is_integer:
                for i in range(len(cust)):
                    for j in range(len(fac)):
                        m.addConstr(x[i,j] <= cust[i].demand * y[j], name=f"link_{i}_{j}")

            m.setParam('TimeLimit', 60)

            self.progress.emit(20)

            m.optimize()

            self.progress.emit(80)

            if m.Status in (GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.SUBOPTIMAL):
                sol_y = {j: y[j].X for j in y}
                sol_x = { (i,j): x[i,j].X for (i,j) in x }
                obj = m.ObjVal if m.SolCount>0 else None

                result = {
                    'status': int(m.Status),
                    'objective': obj,
                    'y': sol_y,
                    'x': sol_x,
                    'dist': {f"{i}_{j}": dist[i,j] for i,j in dist}
                }
                self.finished.emit(result)
            else:
                raise RuntimeError(f"Gurobi failed with status {m.Status}")

        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(str(e) + "\n" + tb)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facility Location & Allocation (PySide6 + Gurobi)")
        self.resize(1100, 700)

        self.data = ProblemData(facilities=[], customers=[])

        self._build_ui()

    def _build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self._build_data_tab(), "Data")
        tabs.addTab(self._build_solver_tab(), "Solve")
        tabs.addTab(self._build_visual_tab(), "Visualization")

        self.setCentralWidget(tabs)

    def _build_data_tab(self):
        widget = QWidget()
        l = QVBoxLayout()

        ctl = QHBoxLayout()
        ctl.addWidget(QLabel("Facilities:"))
        self.fac_count_spin = QSpinBox()
        self.fac_count_spin.setRange(0, 200)
        self.fac_count_spin.setValue(3)
        ctl.addWidget(self.fac_count_spin)

        ctl.addWidget(QLabel("Customers:"))
        self.cust_count_spin = QSpinBox()
        self.cust_count_spin.setRange(0, 500)
        self.cust_count_spin.setValue(6)
        ctl.addWidget(self.cust_count_spin)

        btn_generate = QPushButton("Generate Tables")
        btn_generate.clicked.connect(self._generate_tables)
        ctl.addWidget(btn_generate)

        btn_load = QPushButton("Load JSON")
        btn_load.clicked.connect(self._load_json)
        ctl.addWidget(btn_load)

        btn_save = QPushButton("Save JSON")
        btn_save.clicked.connect(self._save_json)
        ctl.addWidget(btn_save)

        l.addLayout(ctl)

        tables = QHBoxLayout()

        self.fac_table = QTableWidget()
        self.fac_table.setColumnCount(4)
        self.fac_table.setHorizontalHeaderLabels(["x", "y", "fixed_cost", "capacity"])
        tables.addWidget(self._with_label("Facilities (rows = facilities)", self.fac_table))

        self.cust_table = QTableWidget()
        self.cust_table.setColumnCount(3)
        self.cust_table.setHorizontalHeaderLabels(["x", "y", "demand"])
        tables.addWidget(self._with_label("Customers (rows = customers)", self.cust_table))

        l.addLayout(tables)

        param_l = QHBoxLayout()
        param_l.addWidget(QLabel("Transport cost per unit-distance:"))
        self.transport_cost_spin = QDoubleSpinBox()
        self.transport_cost_spin.setRange(0.0, 1e6)
        self.transport_cost_spin.setValue(1.0)
        param_l.addWidget(self.transport_cost_spin)

        param_l.addWidget(QLabel("Model type:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["PLNE", "PL", "PLM"])
        param_l.addWidget(self.model_combo)

        l.addLayout(param_l)

        btn_sample = QPushButton("Load sample data")
        btn_sample.clicked.connect(self._load_sample)
        l.addWidget(btn_sample)

        widget.setLayout(l)
        self._generate_tables()
        return widget

    def _with_label(self, text, widget):
        w = QWidget()
        l = QVBoxLayout()
        l.addWidget(QLabel(text))
        l.addWidget(widget)
        w.setLayout(l)
        return w

    def _generate_tables(self):
        n_fac = self.fac_count_spin.value()
        n_cust = self.cust_count_spin.value()

        self.fac_table.setRowCount(n_fac)
        for i in range(n_fac):
            self._set_item(self.fac_table, i, 0, str(10 * (i+1)))
            self._set_item(self.fac_table, i, 1, str(20 * (i+1) % 100))
            self._set_item(self.fac_table, i, 2, str(100.0))
            self._set_item(self.fac_table, i, 3, str(200.0))

        self.cust_table.setRowCount(n_cust)
        for i in range(n_cust):
            self._set_item(self.cust_table, i, 0, str(5*(i+1)))
            self._set_item(self.cust_table, i, 1, str(12*(i+1) % 100))
            self._set_item(self.cust_table, i, 2, str(20.0))

    def _set_item(self, table, r, c, value):
        it = QTableWidgetItem(value)
        it.setTextAlignment(Qt.AlignCenter)
        table.setItem(r, c, it)

    def _read_tables_into_data(self):
        facs = []
        custs = []
        for i in range(self.fac_table.rowCount()):
            try:
                x = float(self.fac_table.item(i,0).text())
                y = float(self.fac_table.item(i,1).text())
                fc = float(self.fac_table.item(i,2).text())
                cap = float(self.fac_table.item(i,3).text())
            except Exception:
                raise ValueError(f"Invalid facility entry at row {i}")
            facs.append(Facility(id=i, x=x, y=y, fixed_cost=fc, capacity=cap))

        for i in range(self.cust_table.rowCount()):
            try:
                x = float(self.cust_table.item(i,0).text())
                y = float(self.cust_table.item(i,1).text())
                d = float(self.cust_table.item(i,2).text())
            except Exception:
                raise ValueError(f"Invalid customer entry at row {i}")
            custs.append(Customer(id=i, x=x, y=y, demand=d))

        self.data = ProblemData(
            facilities=facs,
            customers=custs,
            transportation_cost_per_distance=self.transport_cost_spin.value(),
            model_type=self.model_combo.currentText()
        )

    def _save_json(self):
        try:
            self._read_tables_into_data()
        except Exception as e:
            QMessageBox.critical(self, "Invalid data", str(e))
            return
        fn, _ = QFileDialog.getSaveFileName(self, "Save dataset", filter="JSON Files (*.json)")
        if not fn:
            return
        payload = {
            'facilities': [asdict(f) for f in self.data.facilities],
            'customers': [asdict(c) for c in self.data.customers],
            'transportation_cost_per_distance': self.data.transportation_cost_per_distance,
            'model_type': self.data.model_type
        }
        with open(fn, 'w') as f:
            json.dump(payload, f, indent=2)
        QMessageBox.information(self, "Saved", f"Saved to {fn}")

    def _load_json(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Load dataset", filter="JSON Files (*.json)")
        if not fn:
            return
        with open(fn, 'r') as f:
            payload = json.load(f)
        facs = [Facility(**fac) for fac in payload.get('facilities', [])]
        custs = [Customer(**c) for c in payload.get('customers', [])]
        self.data = ProblemData(facilities=facs, customers=custs,
                                transportation_cost_per_distance=payload.get('transportation_cost_per_distance', 1.0),
                                model_type=payload.get('model_type', 'PLNE'))
        self.fac_count_spin.setValue(len(facs))
        self.cust_count_spin.setValue(len(custs))
        self._generate_tables()
        for i, f in enumerate(facs):
            self._set_item(self.fac_table, i, 0, str(f.x))
            self._set_item(self.fac_table, i, 1, str(f.y))
            self._set_item(self.fac_table, i, 2, str(f.fixed_cost))
            self._set_item(self.fac_table, i, 3, str(f.capacity))
        for i, c in enumerate(custs):
            self._set_item(self.cust_table, i, 0, str(c.x))
            self._set_item(self.cust_table, i, 1, str(c.y))
            self._set_item(self.cust_table, i, 2, str(c.demand))
        self.transport_cost_spin.setValue(self.data.transportation_cost_per_distance)
        self.model_combo.setCurrentText(self.data.model_type)

    def _load_sample(self):
        facs = [Facility(id=0,x=10,y=10,fixed_cost=150,capacity=150),
                Facility(id=1,x=80,y=20,fixed_cost=120,capacity=130),
                Facility(id=2,x=40,y=90,fixed_cost=200,capacity=200)]
        custs = [Customer(id=i,x=5+15*i,y=10+5*i,demand=20) for i in range(6)]
        self.data = ProblemData(facilities=facs, customers=custs, transportation_cost_per_distance=1.0, model_type='PLNE')
        self.fac_count_spin.setValue(len(facs))
        self.cust_count_spin.setValue(len(custs))
        self._generate_tables()
        for i,f in enumerate(facs):
            self._set_item(self.fac_table,i,0,str(f.x))
            self._set_item(self.fac_table,i,1,str(f.y))
            self._set_item(self.fac_table,i,2,str(f.fixed_cost))
            self._set_item(self.fac_table,i,3,str(f.capacity))
        for i,c in enumerate(custs):
            self._set_item(self.cust_table,i,0,str(c.x))
            self._set_item(self.cust_table,i,1,str(c.y))
            self._set_item(self.cust_table,i,2,str(c.demand))
        self.transport_cost_spin.setValue(1.0)
        self.model_combo.setCurrentText('PLNE')

    def _build_solver_tab(self):
        widget = QWidget()
        l = QVBoxLayout()

        self.btn_solve = QPushButton("Start Solve (Gurobi)")
        self.btn_solve.clicked.connect(self._on_solve)
        l.addWidget(self.btn_solve)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        l.addWidget(self.progress)

        self.results_label = QLabel("No result yet")
        self.results_label.setWordWrap(True)
        l.addWidget(self.results_label)

        widget.setLayout(l)
        return widget

    def _on_solve(self):
        try:
            self._read_tables_into_data()
        except Exception as e:
            QMessageBox.critical(self, "Invalid data", str(e))
            return

        if not GUROBI_AVAILABLE:
            QMessageBox.critical(self, "Gurobi missing", "gurobipy not available. Install Gurobi and the gurobipy package.")
            return

        self.btn_solve.setEnabled(False)
        self.progress.setValue(0)
        self.results_label.setText("Solving...")

        self.solver_thread = SolverThread(self.data)
        self.solver_thread.progress.connect(self.progress.setValue)
        self.solver_thread.finished.connect(self._on_solve_finished)
        self.solver_thread.error.connect(self._on_solve_error)
        self.solver_thread.start()

    def _on_solve_finished(self, result: dict):
        self.btn_solve.setEnabled(True)
        self.progress.setValue(100)
        status = result.get('status')
        obj = result.get('objective')
        if obj is None:
            self.results_label.setText(f"Solver finished with status {status}, but no solution found.")
        else:
            self.results_label.setText(f"Status: {status}. Objective: {obj:.3f}")
            self.last_solution = result
            self._update_visualization_with_solution(result)

    def _on_solve_error(self, err: str):
        self.btn_solve.setEnabled(True)
        QMessageBox.critical(self, "Solver error", str(err))
        self.results_label.setText("Error during solve. See dialog.")

    def _build_visual_tab(self):
        widget = QWidget()
        l = QVBoxLayout()

        self.fig = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        l.addWidget(self.canvas)

        btn_draw = QPushButton("Draw current data")
        btn_draw.clicked.connect(self._draw_current)
        l.addWidget(btn_draw)

        btn_clear = QPushButton("Clear plot")
        btn_clear.clicked.connect(self._clear_plot)
        l.addWidget(btn_clear)

        widget.setLayout(l)
        return widget

    def _clear_plot(self):
        self.ax.cla()
        self.canvas.draw()

    def _draw_current(self):
        try:
            self._read_tables_into_data()
        except Exception as e:
            QMessageBox.critical(self, "Invalid data", str(e))
            return
        self._plot_data(self.data.facilities, self.data.customers)

    def _plot_data(self, facilities: List[Facility], customers: List[Customer]):
        self.ax.cla()
        fx = [f.x for f in facilities]
        fy = [f.y for f in facilities]
        self.ax.scatter(fx, fy, marker='s', s=100, label='Facilities')
        for f in facilities:
            self.ax.annotate(f'F{f.id}', (f.x, f.y), textcoords='offset points', xytext=(5,5))
        cx = [c.x for c in customers]
        cy = [c.y for c in customers]
        self.ax.scatter(cx, cy, marker='o', s=40, label='Customers')
        for c in customers:
            self.ax.annotate(f'C{c.id}', (c.x, c.y), textcoords='offset points', xytext=(5,5))

        self.ax.set_title('Facilities and Customers')
        self.ax.legend()
        self.canvas.draw()

    def _update_visualization_with_solution(self, sol: dict):
        fac = self.data.facilities
        cust = self.data.customers
        self.ax.cla()

        open_facilities = [j for j,v in sol['y'].items() if v > 0.5]
        fx = [fac[j].x for j in open_facilities]
        fy = [fac[j].y for j in open_facilities]
        all_fx = [f.x for f in fac]
        all_fy = [f.y for f in fac]

        self.ax.scatter(all_fx, all_fy, marker='s', s=80, label='Facilities (closed=light)')
        self.ax.scatter(fx, fy, marker='s', s=160, label='Open Facilities')
        for f in fac:
            self.ax.annotate(f'F{f.id}', (f.x, f.y), textcoords='offset points', xytext=(5,5))

        cx = [c.x for c in cust]
        cy = [c.y for c in cust]
        self.ax.scatter(cx, cy, marker='o', s=40, label='Customers')
        for c in cust:
            self.ax.annotate(f'C{c.id}', (c.x, c.y), textcoords='offset points', xytext=(5,5))

        for i in range(len(cust)):
            best_j = None
            best_val = -1
            for j in range(len(fac)):
                val = sol['x'].get((i,j), 0)
                if val > best_val:
                    best_val = val
                    best_j = j
            if best_j is not None and best_val > 1e-6:
                self.ax.plot([cust[i].x, fac[best_j].x], [cust[i].y, fac[best_j].y], linestyle='--')

        self.ax.set_title('Solution: open facilities and allocations')
        self.ax.legend()
        self.canvas.draw()


# ------------------------- Main -------------------------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()