# gui_simple.py
"""
Interface graphique simplifiée - Localisation d'Hôpitaux
Version épurée focalisée sur l'optimisation correcte
"""

import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                                QDoubleSpinBox, QTextEdit, QGroupBox, QSlider)
from PySide6.QtCore import Qt, QThread, Signal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from solve_facility_simple import generate_instance, solve_instance


class SolverThread(QThread):
    """Thread pour optimisation non-bloquante"""
    finished = Signal(dict)
    progress = Signal(str)
    
    def __init__(self, instance, time_limit, mip_gap, alpha, beta):
        super().__init__()
        self.instance = instance
        self.time_limit = time_limit
        self.mip_gap = mip_gap
        self.alpha = alpha
        self.beta = beta
    
    def run(self):
        self.progress.emit("🔄 Optimisation en cours...")
        result = solve_instance(
            self.instance, 
            self.time_limit, 
            self.mip_gap,
            self.alpha,
            self.beta
        )
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 Localisation d'Hôpitaux - PLNE")
        self.setGeometry(100, 100, 1200, 700)
        
        self.instance = None
        self.result = None
        self.solver_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panneau gauche: Contrôles
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left.setMaximumWidth(350)
        
        # Génération instance
        gen_group = QGroupBox("📊 Instance")
        gen_layout = QVBoxLayout()
        
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Villes:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(5, 30)
        self.spin_n.setValue(12)
        param_layout.addWidget(self.spin_n)
        
        param_layout.addWidget(QLabel("Sites:"))
        self.spin_m = QSpinBox()
        self.spin_m.setRange(3, 15)
        self.spin_m.setValue(5)
        param_layout.addWidget(self.spin_m)
        
        gen_layout.addLayout(param_layout)
        
        self.btn_generate = QPushButton("🎲 Générer")
        self.btn_generate.clicked.connect(self.on_generate)
        gen_layout.addWidget(self.btn_generate)
        
        gen_group.setLayout(gen_layout)
        left_layout.addWidget(gen_group)
        
        # Paramètres optimisation
        optim_group = QGroupBox("⚙️ Optimisation")
        optim_layout = QVBoxLayout()
        
        # Time limit
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Temps max (s):"))
        self.spin_time = QSpinBox()
        self.spin_time.setRange(10, 300)
        self.spin_time.setValue(60)
        time_layout.addWidget(self.spin_time)
        optim_layout.addLayout(time_layout)
        
        # MIP Gap
        gap_layout = QHBoxLayout()
        gap_layout.addWidget(QLabel("Gap (%):"))
        self.spin_gap = QDoubleSpinBox()
        self.spin_gap.setRange(0.1, 10)
        self.spin_gap.setValue(1.0)
        self.spin_gap.setSingleStep(0.1)
        gap_layout.addWidget(self.spin_gap)
        optim_layout.addLayout(gap_layout)
        
        # Pondérations
        optim_layout.addWidget(QLabel("\nPondérations:"))
        
        self.label_alpha = QLabel("α (Coût): 0.70")
        optim_layout.addWidget(self.label_alpha)
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(0, 100)
        self.slider_alpha.setValue(70)
        self.slider_alpha.valueChanged.connect(self.update_weights)
        optim_layout.addWidget(self.slider_alpha)
        
        self.label_beta = QLabel("β (Qualité): 0.30")
        optim_layout.addWidget(self.label_beta)
        self.slider_beta = QSlider(Qt.Horizontal)
        self.slider_beta.setRange(0, 100)
        self.slider_beta.setValue(30)
        self.slider_beta.valueChanged.connect(self.update_weights)
        optim_layout.addWidget(self.slider_beta)
        
        optim_group.setLayout(optim_layout)
        left_layout.addWidget(optim_group)
        
        # Bouton optimiser
        self.btn_solve = QPushButton("🚀 OPTIMISER")
        self.btn_solve.setMinimumHeight(50)
        self.btn_solve.setEnabled(False)
        self.btn_solve.clicked.connect(self.on_solve)
        left_layout.addWidget(self.btn_solve)
        
        # Résumé
        summary_group = QGroupBox("📄 Résumé")
        summary_layout = QVBoxLayout()
        self.label_summary = QLabel("Générez une instance pour commencer")
        self.label_summary.setWordWrap(True)
        summary_layout.addWidget(self.label_summary)
        summary_group.setLayout(summary_layout)
        left_layout.addWidget(summary_group)
        
        # Log
        log_group = QGroupBox("📋 Journal")
        log_layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        log_layout.addWidget(self.log)
        log_group.setLayout(log_layout)
        left_layout.addWidget(log_group)
        
        left_layout.addStretch()
        
        # Panneau droit: Visualisation
        right = QWidget()
        right_layout = QVBoxLayout(right)
        
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        right_layout.addWidget(self.canvas)
        
        # Ajouter les panneaux
        layout.addWidget(left)
        layout.addWidget(right, 1)
        
        # Style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
    
    def update_weights(self):
        """Met à jour les pondérations"""
        alpha = self.slider_alpha.value() / 100
        beta = self.slider_beta.value() / 100
        self.label_alpha.setText(f"α (Coût): {alpha:.2f}")
        self.label_beta.setText(f"β (Qualité): {beta:.2f}")
    
    def on_generate(self):
        """Génère une instance"""
        n = self.spin_n.value()
        m = self.spin_m.value()
        
        self.log.append(f"🎲 Génération: {n} villes, {m} sites")
        
        try:
            self.instance = generate_instance(n, m, seed=np.random.randint(1, 1000))
            self.log.append("✅ Instance générée")
            
            summary = f"""
<b>Instance chargée:</b><br>
• Villes: {n}<br>
• Sites: {m}<br>
• Demande totale: {self.instance['demand'].sum()} patients<br>
• Capacité totale: {self.instance['capacity'].sum()}<br>
• Budget: {self.instance['budget']:.0f} €<br>
• Distance max: {self.instance['max_distance']:.0f} km
            """
            self.label_summary.setText(summary)
            
            self.plot_instance()
            self.btn_solve.setEnabled(True)
            
        except Exception as e:
            self.log.append(f"❌ Erreur: {str(e)}")
    
    def plot_instance(self):
        """Affiche l'instance"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Villes
        ax.scatter(
            self.instance['cust_coords'][:, 0],
            self.instance['cust_coords'][:, 1],
            s=self.instance['demand']*3,
            c='blue',
            marker='o',
            alpha=0.6,
            label='Villes'
        )
        
        # Sites
        ax.scatter(
            self.instance['site_coords'][:, 0],
            self.instance['site_coords'][:, 1],
            s=200,
            c='green',
            marker='s',
            alpha=0.6,
            label='Sites candidats'
        )
        
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_title('Instance du Problème', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def on_solve(self):
        """Lance l'optimisation"""
        if self.instance is None:
            return
        
        self.btn_solve.setEnabled(False)
        
        time_limit = self.spin_time.value()
        mip_gap = self.spin_gap.value() / 100
        alpha = self.slider_alpha.value() / 100
        beta = self.slider_beta.value() / 100
        
        self.log.append(f"🚀 Optimisation (α={alpha:.2f}, β={beta:.2f})")
        
        self.solver_thread = SolverThread(
            self.instance, time_limit, mip_gap, alpha, beta
        )
        self.solver_thread.progress.connect(self.log.append)
        self.solver_thread.finished.connect(self.on_solve_finished)
        self.solver_thread.start()
    
    def on_solve_finished(self, result):
        """Traite les résultats"""
        self.btn_solve.setEnabled(True)
        self.result = result
        
        if result.get('objective') is None:
            self.log.append("❌ Problème non résolu")
            return
        
        self.log.append(f"✅ Solution trouvée!")
        self.log.append(f"📊 Objectif: {result['objective']:.2f}")
        self.log.append(f"🏥 Ouverts: {result['n_opened']}/{self.instance['m_sites']}")
        self.log.append(f"💰 Coût: {result['total_cost']:.2f} €")
        self.log.append(f"⏱️ Temps: {result['runtime']:.2f}s")
        
        self.plot_solution()
    
    def plot_solution(self):
        """Affiche la solution"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Villes
        ax.scatter(
            self.instance['cust_coords'][:, 0],
            self.instance['cust_coords'][:, 1],
            s=self.instance['demand']*3,
            c='blue',
            marker='o',
            alpha=0.6,
            label='Villes'
        )
        
        # Sites ouverts
        opened = self.result['opened_sites']
        closed = [j for j in range(self.instance['m_sites']) if j not in opened]
        
        if opened:
            ax.scatter(
                self.instance['site_coords'][opened, 0],
                self.instance['site_coords'][opened, 1],
                s=300,
                c='green',
                marker='s',
                label='Hôpitaux ouverts',
                edgecolors='black',
                linewidths=2
            )
        
        if closed:
            ax.scatter(
                self.instance['site_coords'][closed, 0],
                self.instance['site_coords'][closed, 1],
                s=150,
                c='gray',
                marker='s',
                alpha=0.3,
                label='Sites fermés'
            )
        
        # Affectations
        for i in range(self.instance['n_customers']):
            for j in range(self.instance['m_sites']):
                if self.result['x'][i][j] == 1:
                    ax.plot(
                        [self.instance['cust_coords'][i, 0], 
                         self.instance['site_coords'][j, 0]],
                        [self.instance['cust_coords'][i, 1], 
                         self.instance['site_coords'][j, 1]],
                        'r-',
                        alpha=0.4,
                        linewidth=1.5
                    )
        
        # Annotations
        for j in opened:
            usage = sum(
                self.instance['demand'][i] * self.result['x'][i][j] 
                for i in range(self.instance['n_customers'])
            )
            usage_pct = (usage / self.instance['capacity'][j] * 100) if self.instance['capacity'][j] > 0 else 0
            ax.annotate(
                f"H{j}\n{usage_pct:.0f}%",
                (self.instance['site_coords'][j, 0], self.instance['site_coords'][j, 1]),
                fontsize=9,
                fontweight='bold',
                ha='center'
            )
        
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_title('Solution Optimale', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
