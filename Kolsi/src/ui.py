import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLabel, QTabWidget, QMessageBox, QHeaderView, QSplitter, 
                             QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt

# Import Logic
from model import GasOptimizationModel, ArcData, CommodityData

# --- Threading Class (Requirement: "Contrôle du calcul non bloquant") ---
class SolverThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, model_instance, arcs, comms):
        super().__init__()
        self.model = model_instance
        self.arcs = arcs
        self.comms = comms

    def run(self):
        try:
            success, obj, res = self.model.solve_model(self.arcs, self.comms)
            if success:
                self.finished.emit({'status': 'Optimal', 'cost': obj, 'data': res})
            else:
                self.error.emit("Infeasible: The network cannot satisfy all demands with current capacities.")
        except Exception as e:
            self.error.emit(str(e))

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projet RO - Distribution Gaz Naturel (PLM)")
        self.resize(1300, 800)
        
        self.model_wrapper = GasOptimizationModel()
        self.init_ui()

    def init_ui(self):
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Header Area
        header = QLabel("Application 3: Energy - Natural Gas Distribution Optimization")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 5px;")
        main_layout.addWidget(header)

        # 2. Splitter (Input Left, Graph Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- LEFT SIDE: INPUTS ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Tabs for Data Entry
        self.tabs = QTabWidget()
        
        # Tab 1: Network (Arcs)
        self.arcs_tab = QWidget()
        arc_layout = QVBoxLayout(self.arcs_tab)
        self.arcs_table = self.create_table(["Source", "Target", "Capacity", "Var Cost", "Fixed Cost"])
        arc_layout.addWidget(self.arcs_table)
        arc_layout.addLayout(self.create_buttons(self.arcs_table))
        self.tabs.addTab(self.arcs_tab, "Pipeline Network")

        # Tab 2: Demands (Commodities)
        self.comm_tab = QWidget()
        comm_layout = QVBoxLayout(self.comm_tab)
        self.comm_table = self.create_table(["ID", "Origin", "Destination", "Quantity", "Quality Name"])
        comm_layout.addWidget(self.comm_table)
        comm_layout.addLayout(self.create_buttons(self.comm_table))
        self.tabs.addTab(self.comm_tab, "Gas Demands")

        left_layout.addWidget(self.tabs)

        # Control Box
        controls = QGroupBox("Operations")
        ctrl_layout = QHBoxLayout(controls)
        
        self.btn_load = QPushButton("Load Sample Data")
        self.btn_load.clicked.connect(self.load_sample)
        
        self.btn_preview = QPushButton("Preview Graph")
        self.btn_preview.clicked.connect(self.preview_graph)

        self.btn_solve = QPushButton("Solve (Gurobi)")
        self.btn_solve.setStyleSheet("font-weight: bold;")
        self.btn_solve.clicked.connect(self.start_optimization)

        ctrl_layout.addWidget(self.btn_load)
        ctrl_layout.addWidget(self.btn_preview)
        ctrl_layout.addWidget(self.btn_solve)
        left_layout.addWidget(controls)

        # --- RIGHT SIDE: VISUALIZATION ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("padding: 5px; background: #f0f0f0; border: 1px solid #ccc;")
        right_layout.addWidget(self.status_label)

        self.figure = Figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 800])

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def create_buttons(self, table):
        layout = QHBoxLayout()
        btn_add = QPushButton("+ Add Row")
        btn_add.clicked.connect(lambda: table.insertRow(table.rowCount()))
        btn_rem = QPushButton("- Remove Selected")
        btn_rem.clicked.connect(lambda: self.remove_row(table))
        layout.addWidget(btn_add)
        layout.addWidget(btn_rem)
        layout.addStretch()
        return layout

    def remove_row(self, table):
        rows = sorted(set(index.row() for index in table.selectedIndexes()), reverse=True)
        for row in rows:
            table.removeRow(row)

    def load_sample(self):
        # Arcs
        data_arcs = [
            ("S1", "A", 100, 1, 50), ("S1", "B", 100, 1.5, 50),
            ("S2", "B", 100, 1, 50), ("A", "C", 80, 1, 20),
            ("B", "C", 80, 1, 20),   ("B", "D", 80, 1.5, 20),
            ("C", "T1", 100, 1, 30), ("D", "T2", 100, 1, 30)
        ]
        self.arcs_table.setRowCount(0)
        self.arcs_table.setRowCount(len(data_arcs))
        for i, row in enumerate(data_arcs):
            for j, val in enumerate(row):
                self.arcs_table.setItem(i, j, QTableWidgetItem(str(val)))

        # Commodities (Gas Types)
        data_comm = [
            ("K1", "S1", "T1", 30, "H-Gas"),
            ("K2", "S2", "T2", 40, "L-Gas"),
            ("K3", "S1", "T2", 20, "M-Gas")
        ]
        self.comm_table.setRowCount(0)
        self.comm_table.setRowCount(len(data_comm))
        for i, row in enumerate(data_comm):
            for j, val in enumerate(row):
                self.comm_table.setItem(i, j, QTableWidgetItem(str(val)))
        
        self.preview_graph()

    def get_data(self):
        arcs = []
        for i in range(self.arcs_table.rowCount()):
            try:
                s, t = self.arcs_table.item(i, 0).text(), self.arcs_table.item(i, 1).text()
                c = float(self.arcs_table.item(i, 2).text())
                vc = float(self.arcs_table.item(i, 3).text())
                fc = float(self.arcs_table.item(i, 4).text())
                if s and t: arcs.append(ArcData(s, t, c, vc, fc))
            except: continue

        comms = []
        colors = {"H-Gas": "blue", "L-Gas": "orange", "M-Gas": "green"}
        for i in range(self.comm_table.rowCount()):
            try:
                cid = self.comm_table.item(i, 0).text()
                o, d = self.comm_table.item(i, 1).text(), self.comm_table.item(i, 2).text()
                q = float(self.comm_table.item(i, 3).text())
                qual = self.comm_table.item(i, 4).text()
                col = colors.get(qual, "black")
                if cid: comms.append(CommodityData(cid, o, d, q, qual, col))
            except: continue
            
        return arcs, comms

    def preview_graph(self):
        arcs, _ = self.get_data()
        self.draw_network(arcs, None, None)

    def start_optimization(self):
        arcs, comms = self.get_data()
        if not arcs or not comms:
            QMessageBox.warning(self, "Data Error", "Please verify your data inputs.")
            return

        self.btn_solve.setEnabled(False)
        self.status_label.setText("Status: Gurobi Running...")
        
        # Threading handles the "Non-blocking" requirement
        self.thread = SolverThread(self.model_wrapper, arcs, comms)
        self.thread.finished.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_success(self, result):
        self.btn_solve.setEnabled(True)
        self.status_label.setText(f"Status: Optimal Solution Found. Cost: {result['cost']:.2f}")
        arcs, comms = self.get_data()
        self.draw_network(arcs, result['data'], comms)

    def on_error(self, msg):
        self.btn_solve.setEnabled(True)
        self.status_label.setText("Status: Error")
        QMessageBox.critical(self, "Solver Error", msg)

    def draw_network(self, arcs, res, comms):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        G = nx.DiGraph()
        for a in arcs:
            G.add_edge(a.source, a.target)

        pos = nx.spring_layout(G, seed=42)
        
        # Draw base
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightgrey', node_size=500, edgecolors='black')
        nx.draw_networkx_labels(G, pos, ax=ax)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='lightgrey', arrows=True)

        if res and comms:
            comm_map = {c.cid: c.color for c in comms}
            
            # Group flows by edge to offset them (visualizing multiple qualities in one pipe)
            edge_flows = {}
            for f in res['flows']:
                key = (f['source'], f['target'])
                if key not in edge_flows: edge_flows[key] = []
                edge_flows[key].append(f)

            for (u, v), flows in edge_flows.items():
                # If multiple flows, offset logic could go here, 
                # for now we layer them with different widths/colors or just show dominant
                # This explicitly shows "Different qualities via same pipeline"
                for i, flow in enumerate(flows):
                    rad = 0.1 * (i + 1) # Curve the line slightly if multiple commodities
                    color = comm_map.get(flow['commodity'], 'black')
                    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u,v)], 
                                         edge_color=color, width=2, 
                                         connectionstyle=f'arc3,rad={rad}')
                    # Label text
                    mid_x = (pos[u][0] + pos[v][0]) / 2
                    mid_y = (pos[u][1] + pos[v][1]) / 2 + (i*0.05)
                    ax.text(mid_x, mid_y, f"{flow['amount']:.0f}", color=color, fontweight='bold')

        ax.set_title("Natural Gas Distribution Network")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Clean, standard look (Windows/Linux friendly)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())