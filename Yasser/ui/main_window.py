import random
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
                             QLabel, QGroupBox, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt

from .workers import SolverWorker
from .visualization import MplCanvas


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Localisation Usines & Affectation")
        self.resize(1200, 800)
        
        # Données stockées
        self.markets_data = []
        self.sites_data = []
        self.costs_matrix = []

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 1. Zone de contrôle (Haut)
        control_group = QGroupBox("Contrôles")
        control_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Générer Données Aléatoires")
        self.btn_generate.clicked.connect(self.generate_random_data)
        self.btn_solve = QPushButton("Lancer l'Optimisation")
        self.btn_solve.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_solve.clicked.connect(self.solve_problem)
        
        control_layout.addWidget(self.btn_generate)
        control_layout.addWidget(self.btn_solve)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 2. Zone principale (Onglets pour données et résultats)
        self.tabs = QTabWidget()
        
        # Onglet Données
        tab_data = QWidget()
        layout_data = QHBoxLayout(tab_data)
        
        # Table Marchés
        self.table_markets = QTableWidget(0, 4)
        self.table_markets.setHorizontalHeaderLabels(["ID", "Demande", "X", "Y"])
        layout_data.addWidget(self.create_group("Marchés (Demande)", self.table_markets))
        
        # Table Sites
        self.table_sites = QTableWidget(0, 5)
        self.table_sites.setHorizontalHeaderLabels(["ID", "Capacité", "Coût Fixe", "X", "Y"])
        layout_data.addWidget(self.create_group("Sites Potentiels (Usines)", self.table_sites))
        
        self.tabs.addTab(tab_data, "1. Données d'Entrée")
        
        # Onglet Résultats
        tab_res = QWidget()
        layout_res = QHBoxLayout(tab_res)
        
        # Texte Résultats
        self.lbl_results = QLabel("En attente de résolution...")
        self.lbl_results.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lbl_results.setWordWrap(True)
        self.lbl_results.setStyleSheet("font-size: 14px; padding: 10px; border: 1px solid #ccc;")
        layout_res.addWidget(self.lbl_results, 1)
        
        # Graphique
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout_res.addWidget(self.canvas, 2)
        
        self.tabs.addTab(tab_res, "2. Résultats & Visualisation")
        
        layout.addWidget(self.tabs)

    def create_group(self, title, widget):
        gb = QGroupBox(title)
        l = QVBoxLayout()
        l.addWidget(widget)
        gb.setLayout(l)
        return gb

    def generate_random_data(self):
        """Génère un scénario aléatoire pour tester l'appli."""
        num_markets = 10
        num_sites = 5
        
        self.markets_data = []
        self.sites_data = []
        
        # Remplir Table Marchés
        self.table_markets.setRowCount(num_markets)
        for i in range(num_markets):
            d = random.randint(50, 150)
            x, y = random.randint(0, 100), random.randint(0, 100)
            self.markets_data.append({'id': i, 'demand': d, 'x': x, 'y': y})
            self.table_markets.setItem(i, 0, QTableWidgetItem(str(i)))
            self.table_markets.setItem(i, 1, QTableWidgetItem(str(d)))
            self.table_markets.setItem(i, 2, QTableWidgetItem(str(x)))
            self.table_markets.setItem(i, 3, QTableWidgetItem(str(y)))

        # Remplir Table Sites
        self.table_sites.setRowCount(num_sites)
        for j in range(num_sites):
            cap = random.randint(200, 500)
            fc = random.randint(1000, 5000)
            x, y = random.randint(0, 100), random.randint(0, 100)
            self.sites_data.append({'id': j, 'capacity': cap, 'fixed_cost': fc, 'x': x, 'y': y})
            self.table_sites.setItem(j, 0, QTableWidgetItem(str(j)))
            self.table_sites.setItem(j, 1, QTableWidgetItem(str(cap)))
            self.table_sites.setItem(j, 2, QTableWidgetItem(str(fc)))
            self.table_sites.setItem(j, 3, QTableWidgetItem(str(x)))
            self.table_sites.setItem(j, 4, QTableWidgetItem(str(y)))
            
        # Calcul de la matrice des coûts (Distance Euclidienne * Coût au km)
        self.costs_matrix = np.zeros((num_sites, num_markets))
        for j in range(num_sites):
            for i in range(num_markets):
                s = self.sites_data[j]
                m = self.markets_data[i]
                dist = np.sqrt((s['x']-m['x'])**2 + (s['y']-m['y'])**2)
                self.costs_matrix[j][i] = round(dist * 2, 2)  # Disons 2 TND par km

        QMessageBox.information(self, "Info", "Données aléatoires générées avec succès.")

    def solve_problem(self):
        if not self.markets_data or not self.sites_data:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord générer ou saisir des données.")
            return

        self.btn_solve.setEnabled(False)
        self.lbl_results.setText("Calcul en cours avec Gurobi...")
        
        # Lancement du Thread
        self.worker = SolverWorker(self.markets_data, self.sites_data, self.costs_matrix)
        self.worker.finished_signal.connect(self.on_optimization_finished)
        self.worker.start()

    def on_optimization_finished(self, results):
        self.btn_solve.setEnabled(True)
        self.tabs.setCurrentIndex(1)  # Basculer sur l'onglet résultat
        
        if "Error" in str(results.get('status')):
            self.lbl_results.setText(f"Erreur: {results['status']}")
            return

        # Affichage Texte
        txt = f"<b>Statut:</b> {results['status']}<br>"
        txt += f"<b>Coût Total Minimal:</b> {results['obj_val']:.2f} TND<br><br>"
        txt += "<b>Usines Ouvertes:</b><br>"
        for idx in results['sites_open']:
            site = self.sites_data[idx]
            txt += f"- Usine {idx} (Cap: {site['capacity']}, Coût Fixe: {site['fixed_cost']})<br>"
        
        self.lbl_results.setText(txt)
        
        # Visualisation Graphique
        self.plot_solution(results)

    def plot_solution(self, results):
        self.canvas.axes.clear()
        
        # 1. Dessiner tous les sites potentiels (Carrés)
        for j, site in enumerate(self.sites_data):
            color = 'green' if j in results['sites_open'] else 'gray'
            marker = 's'  # square
            size = 100 if j in results['sites_open'] else 50
            self.canvas.axes.scatter(site['x'], site['y'], c=color, marker=marker, s=size, label=f'Usine {j}' if j==0 else "")
            self.canvas.axes.text(site['x'], site['y']+2, f"U{j}", fontsize=9, color=color)

        # 2. Dessiner les marchés (Cercles bleus)
        for i, market in enumerate(self.markets_data):
            self.canvas.axes.scatter(market['x'], market['y'], c='blue', marker='o', s=30)
            self.canvas.axes.text(market['x'], market['y']-3, f"M{i}", fontsize=8)

        # 3. Dessiner les flux (Lignes)
        if 'flows' in results:
            for flow in results['flows']:
                u_idx = flow['factory_idx']
                m_idx = flow['market_idx']
                u = self.sites_data[u_idx]
                m = self.markets_data[m_idx]
                
                # Épaisseur de la ligne selon la quantité
                width = 1 + (flow['qty'] / 20) 
                self.canvas.axes.plot([u['x'], m['x']], [u['y'], m['y']], 'g--', alpha=0.5, linewidth=width)

        self.canvas.axes.set_title("Carte de Localisation et Allocation Optimale")
        self.canvas.draw()
