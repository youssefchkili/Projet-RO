import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QSpinBox, QTextEdit, QCheckBox, QHeaderView,
                             QGroupBox, QGridLayout, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from visualization import RouteVisualizer

API_URL = "http://localhost:5000/api"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Routage du Personnel - Maintenance")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #e2e8f0;
                padding: 10px 20px;
                margin-right: 4px;
                border-radius: 8px 8px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #2563eb;
                color: white;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
            QPushButton.success {
                background-color: #10b981;
            }
            QPushButton.success:hover {
                background-color: #059669;
            }
            QPushButton.danger {
                background-color: #ef4444;
            }
            QPushButton.danger:hover {
                background-color: #dc2626;
            }
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #1e293b;
            }
            QGroupBox {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #1e293b;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_dashboard_tab(), "📊 Tableau de bord")
        self.tabs.addTab(self.create_technicians_tab(), "👷 Techniciens")
        self.tabs.addTab(self.create_tasks_tab(), "📋 Tâches")
        self.tabs.addTab(self.create_routes_tab(), "🚗 Tournées")
        
        layout.addWidget(self.tabs)
        
        # Auto-refresh data (reduced frequency for performance)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial data load
        self.refresh_data()
    
    def create_header(self):
        header = QWidget()
        header.setStyleSheet("background-color: white; padding: 15px;")
        layout = QHBoxLayout(header)
        
        # Title
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🔧 Routage du Personnel")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        
        subtitle = QLabel("Gestion des tournées de maintenance")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #64748b;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_widget)
        layout.addStretch()
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        
        # Optimize button
        optimize_btn = QPushButton("🚀 Optimiser les tournées")
        optimize_btn.setProperty("class", "success")
        optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        optimize_btn.clicked.connect(self.optimize_routes)
        buttons_layout.addWidget(optimize_btn)
        
        # Reset button
        reset_btn = QPushButton("🔄 Réinitialiser les tâches")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        reset_btn.clicked.connect(self.reset_tasks)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
        return header
    
    def create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Stats grid
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        self.stat_cards = {}
        stats = [
            ("techs", "👷 Techniciens disponibles", "#2563eb"),
            ("pending", "⏳ Tâches en attente", "#f59e0b"),
            ("assigned", "✅ Tâches assignées", "#10b981"),
            ("high_priority", "🔥 Priorité haute", "#ef4444")
        ]
        
        for idx, (key, label, color) in enumerate(stats):
            card = self.create_stat_card(label, "0", color)
            self.stat_cards[key] = card
            stats_layout.addWidget(card, idx // 2, idx % 2)
        
        layout.addWidget(stats_widget)
        
        # Info section
        self.info_label = QLabel("Chargement des données...")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            color: #1e293b;
            font-size: 13px;
        """)
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        return widget
    
    def create_stat_card(self, title, value, color):
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background: white;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("value")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet("color: #64748b;")
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return card
    
    def create_technicians_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Nouveau technicien")
        add_btn.clicked.connect(self.add_technician)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Table
        self.tech_table = QTableWidget()
        self.tech_table.setColumnCount(6)
        self.tech_table.setHorizontalHeaderLabels([
            "Nom", "Compétences", "Capacité/jour", "Disponible", "Actions", "ID"
        ])
        self.tech_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tech_table.setColumnHidden(5, True)  # Hide ID column
        self.tech_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tech_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.tech_table)
        
        return widget
    
    def create_tasks_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Nouvelle tâche")
        add_btn.clicked.connect(self.add_task)
        toolbar.addWidget(add_btn)
        
        # Filter
        toolbar.addWidget(QLabel("Filtrer:"))
        self.task_filter = QComboBox()
        self.task_filter.addItems(["Toutes", "En attente", "Assignées", "Terminées"])
        self.task_filter.currentTextChanged.connect(self.refresh_data)
        toolbar.addWidget(self.task_filter)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(8)
        self.task_table.setHorizontalHeaderLabels([
            "Titre", "Compétence", "Priorité", "Durée (min)", "Statut", "Assigné à", "Actions", "ID"
        ])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.task_table.setColumnHidden(7, True)  # Hide ID column
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.task_table)
        
        return widget
    
    def create_routes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.setProperty("class", "danger")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        reset_btn.clicked.connect(self.clear_routes)
        toolbar.addWidget(reset_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Splitter for text and visualization
        splitter = QSplitter(Qt.Horizontal)
        
        # Routes display (Text)
        self.routes_text = QTextEdit()
        self.routes_text.setReadOnly(True)
        self.routes_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 12px;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        splitter.addWidget(self.routes_text)
        
        # Visualization
        self.visualizer = RouteVisualizer()
        splitter.addWidget(self.visualizer)
        
        # Set initial sizes (40% text, 60% visualizer)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        
        return widget
    
    def refresh_data(self):
        """Refresh all data from API"""
        try:
            # Get technicians
            response = requests.get(f"{API_URL}/technicians")
            if response.status_code == 200:
                self.technicians = response.json()
                self.update_technicians_table()
            
            # Get tasks
            response = requests.get(f"{API_URL}/tasks")
            if response.status_code == 200:
                self.tasks = response.json()
                self.update_tasks_table()
            
            # Get routes
            response = requests.get(f"{API_URL}/routes")
            if response.status_code == 200:
                self.routes = response.json()
                self.update_routes_display()
            
            # Update dashboard
            self.update_dashboard()
            
        except requests.exceptions.ConnectionError:
            QMessageBox.warning(self, "Erreur", 
                              "Impossible de se connecter au serveur.\n"
                              "Assurez-vous que le backend est démarré.")
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    def update_dashboard(self):
        """Update dashboard statistics"""
        if not hasattr(self, 'technicians') or not hasattr(self, 'tasks'):
            return
        
        available_techs = len([t for t in self.technicians if t.get('available')])
        pending_tasks = len([t for t in self.tasks if t.get('status') == 'pending'])
        assigned_tasks = len([t for t in self.tasks if t.get('status') == 'assigned'])
        high_priority = len([t for t in self.tasks if t.get('priority') == 'high' and t.get('status') == 'pending'])
        
        # Update stat cards
        self.stat_cards['techs'].findChild(QLabel, "value").setText(f"{available_techs}/{len(self.technicians)}")
        self.stat_cards['pending'].findChild(QLabel, "value").setText(str(pending_tasks))
        self.stat_cards['assigned'].findChild(QLabel, "value").setText(str(assigned_tasks))
        self.stat_cards['high_priority'].findChild(QLabel, "value").setText(str(high_priority))
        
        # Update info message
        if pending_tasks > 0 and available_techs > 0:
            msg = f"✅ Prêt à optimiser!\n\n"
            msg += f"Vous avez {pending_tasks} tâche(s) en attente et {available_techs} technicien(s) disponible(s)."
            if high_priority > 0:
                msg += f"\n{high_priority} tâche(s) sont prioritaire(s)."
            msg += "\n\nCliquez sur 'Optimiser les tournées' pour générer automatiquement les routes optimales."
        elif pending_tasks == 0:
            msg = "✅ Toutes les tâches sont traitées.\n\nAucune tâche en attente d'assignation."
        elif available_techs == 0:
            msg = f"⚠️ Attention!\n\nAucun technicien disponible pour les {pending_tasks} tâche(s) en attente."
        else:
            msg = "Chargement des données..."
        
        self.info_label.setText(msg)
    
    def update_technicians_table(self):
        """Update technicians table"""
        self.tech_table.setRowCount(0)
        
        for tech in self.technicians:
            row = self.tech_table.rowCount()
            self.tech_table.insertRow(row)
            
            self.tech_table.setItem(row, 0, QTableWidgetItem(tech['name']))
            self.tech_table.setItem(row, 1, QTableWidgetItem(", ".join(tech['skills'])))
            self.tech_table.setItem(row, 2, QTableWidgetItem(str(tech['maxTasksPerDay'])))
            self.tech_table.setItem(row, 3, QTableWidgetItem("✅ Oui" if tech['available'] else "❌ Non"))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, t=tech: self.edit_technician(t))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("background-color: #ef4444;")
            delete_btn.clicked.connect(lambda checked, t=tech: self.delete_technician(t['id']))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.tech_table.setCellWidget(row, 4, actions_widget)
            self.tech_table.setItem(row, 5, QTableWidgetItem(tech['id']))
    
    def update_tasks_table(self):
        """Update tasks table"""
        self.task_table.setRowCount(0)
        
        # Apply filter
        filter_text = self.task_filter.currentText()
        filtered_tasks = self.tasks
        
        if filter_text == "En attente":
            filtered_tasks = [t for t in self.tasks if t['status'] == 'pending']
        elif filter_text == "Assignées":
            filtered_tasks = [t for t in self.tasks if t['status'] == 'assigned']
        elif filter_text == "Terminées":
            filtered_tasks = [t for t in self.tasks if t['status'] == 'completed']
        
        for task in filtered_tasks:
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)
            
            self.task_table.setItem(row, 0, QTableWidgetItem(task['title']))
            self.task_table.setItem(row, 1, QTableWidgetItem(task['requiredSkill']))
            
            # Priority with color
            priority_item = QTableWidgetItem(task['priority'].upper())
            if task['priority'] == 'high':
                priority_item.setBackground(QColor(254, 226, 226))
                priority_item.setForeground(QColor(153, 27, 27))
            elif task['priority'] == 'medium':
                priority_item.setBackground(QColor(254, 243, 199))
                priority_item.setForeground(QColor(146, 64, 14))
            else:
                priority_item.setBackground(QColor(219, 234, 254))
                priority_item.setForeground(QColor(30, 64, 175))
            self.task_table.setItem(row, 2, priority_item)
            
            self.task_table.setItem(row, 3, QTableWidgetItem(str(task['duration'])))
            
            # Status with color
            status_text = {'pending': 'En attente', 'assigned': 'Assignée', 'completed': 'Terminée'}[task['status']]
            status_item = QTableWidgetItem(status_text)
            if task['status'] == 'pending':
                status_item.setBackground(QColor(254, 243, 199))
            elif task['status'] == 'assigned':
                status_item.setBackground(QColor(224, 231, 255))
            else:
                status_item.setBackground(QColor(209, 250, 229))
            self.task_table.setItem(row, 4, status_item)
            
            self.task_table.setItem(row, 5, QTableWidgetItem(task.get('assignedTo', '') or '-'))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, t=task: self.edit_task(t))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("background-color: #ef4444;")
            delete_btn.clicked.connect(lambda checked, t=task: self.delete_task(t['id']))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.task_table.setCellWidget(row, 6, actions_widget)
            self.task_table.setItem(row, 7, QTableWidgetItem(task['id']))
    
    def update_routes_display(self):
        """Update routes display"""
        if not self.routes:
            self.routes_text.setHtml("""
                <div style='text-align: center; padding: 40px; color: #64748b;'>
                    <h2>🚀 Aucune tournée planifiée</h2>
                    <p>Cliquez sur 'Optimiser les tournées' pour générer automatiquement<br>
                    les tournées en fonction des compétences et des distances.</p>
                </div>
            """)
            # Reset visualization
            if hasattr(self, 'visualizer'):
                self.visualizer.show_placeholder()
            return
        
        latest_route = self.routes[-1]
        html = f"""
        <style>
            body {{ font-family: Arial; }}
            .header {{ background: #f1f5f9; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
            .route {{ background: white; border: 2px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
            .route-header {{ color: #1e293b; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
            .task {{ background: #f8fafc; padding: 10px; margin: 8px 0; border-left: 4px solid #2563eb; border-radius: 4px; }}
            .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }}
            .badge-high {{ background: #fee2e2; color: #991b1b; }}
            .badge-medium {{ background: #fef3c7; color: #92400e; }}
            .badge-low {{ background: #dbeafe; color: #1e40af; }}
        </style>
        """
        
        total_distance = sum(r['totalDistance'] for r in latest_route['routes'])
        total_duration = sum(r['totalDuration'] for r in latest_route['routes'])
        
        html += f"""
        <div class='header'>
            <strong>📊 Résumé de l'optimisation</strong><br>
            🚗 {len(latest_route['routes'])} tournée(s) | 
            ✅ {latest_route['assignedTasks']}/{latest_route['totalTasks']} tâches assignées | 
            📏 {total_distance:.1f} km total | 
            ⏱️ {total_duration // 60}h {total_duration % 60}min
        </div>
        """
        
        for route in latest_route['routes']:
            html += f"""
            <div class='route'>
                <div class='route-header'>
                    👷 {route['technicianName']} - {route['taskCount']} tâche(s) | 
                    📏 {route['totalDistance']} km | ⏱️ {route['totalDuration'] // 60}h {route['totalDuration'] % 60}min
                </div>
            """
            
            for idx, task in enumerate(route['tasks'], 1):
                priority_class = f"badge-{task['priority']}"
                html += f"""
                <div class='task'>
                    <strong>[{idx}] {task['title']}</strong> 
                    <span class='badge {priority_class}'>{task['priority'].upper()}</span><br>
                    🔧 {task['requiredSkill']} | ⏱️ {task['duration']}min<br>
                    📍 {task['location'].get('address', 'Adresse non spécifiée')}
                """
                if task.get('distanceFromPrevious'):
                    html += f"<br>🚗 {task['distanceFromPrevious']:.2f} km depuis la tâche précédente"
                html += "</div>"
            
            html += "</div>"
        
        self.routes_text.setHtml(html)
        
        # Update visualization
        if hasattr(self, 'visualizer') and hasattr(self, 'technicians'):
            self.visualizer.update_routes(latest_route['routes'], self.technicians)
    
    def optimize_routes(self):
        """Optimize routes"""
        try:
            response = requests.post(f"{API_URL}/routes/optimize")
            if response.status_code == 200:
                QMessageBox.information(self, "Succès", "Les tournées ont été optimisées avec succès!")
                self.tabs.setCurrentIndex(3)  # Switch to routes tab
                self.refresh_data()
            else:
                error = response.json().get('detail', 'Erreur inconnue')
                QMessageBox.warning(self, "Erreur", f"Erreur lors de l'optimisation:\n{error}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def reset_tasks(self):
        """Reset all tasks to pending status"""
        reply = QMessageBox.question(self, "Confirmation",
                                    "Réinitialiser toutes les tâches à l'état 'En attente'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Get all tasks and reset them
                response = requests.get(f"{API_URL}/tasks")
                if response.status_code == 200:
                    tasks = response.json()
                    for task in tasks:
                        requests.put(f"{API_URL}/tasks/{task['id']}", 
                                   json={"status": "pending", "assignedTo": None})
                    
                    # Clear routes
                    requests.delete(f"{API_URL}/routes")
                    
                    QMessageBox.information(self, "Succès", "Toutes les tâches ont été réinitialisées!")
                    self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def clear_routes(self):
        """Clear all routes"""
        reply = QMessageBox.question(self, "Confirmation",
                                    "Êtes-vous sûr de vouloir réinitialiser toutes les tournées?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                requests.delete(f"{API_URL}/routes")
                QMessageBox.information(self, "Succès", "Les tournées ont été réinitialisées!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def add_technician(self):
        dialog = TechnicianDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                response = requests.post(f"{API_URL}/technicians", json=data)
                if response.status_code == 201:
                    QMessageBox.information(self, "Succès", "Technicien créé avec succès!")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Erreur", "Erreur lors de la création")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def edit_technician(self, tech):
        dialog = TechnicianDialog(self, tech)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                response = requests.put(f"{API_URL}/technicians/{tech['id']}", json=data)
                if response.status_code == 200:
                    QMessageBox.information(self, "Succès", "Technicien modifié avec succès!")
                    self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def delete_technician(self, tech_id):
        reply = QMessageBox.question(self, "Confirmation",
                                    "Êtes-vous sûr de vouloir supprimer ce technicien?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                requests.delete(f"{API_URL}/technicians/{tech_id}")
                QMessageBox.information(self, "Succès", "Technicien supprimé!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                response = requests.post(f"{API_URL}/tasks", json=data)
                if response.status_code == 201:
                    QMessageBox.information(self, "Succès", "Tâche créée avec succès!")
                    self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def edit_task(self, task):
        dialog = TaskDialog(self, task)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                response = requests.put(f"{API_URL}/tasks/{task['id']}", json=data)
                if response.status_code == 200:
                    QMessageBox.information(self, "Succès", "Tâche modifiée avec succès!")
                    self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def delete_task(self, task_id):
        reply = QMessageBox.question(self, "Confirmation",
                                    "Êtes-vous sûr de vouloir supprimer cette tâche?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                requests.delete(f"{API_URL}/tasks/{task_id}")
                QMessageBox.information(self, "Succès", "Tâche supprimée!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


class TechnicianDialog(QDialog):
    def __init__(self, parent=None, technician=None):
        super().__init__(parent)
        self.technician = technician
        self.setWindowTitle("Modifier technicien" if technician else "Nouveau technicien")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Jean Dupont")
        form.addRow("Nom complet *:", self.name_input)
        
        # Skills checkboxes
        skills_widget = QWidget()
        skills_layout = QGridLayout(skills_widget)
        self.skill_checks = {}
        skills = ['plomberie', 'électricité', 'climatisation', 'chauffage', 'serrurerie', 'peinture']
        for idx, skill in enumerate(skills):
            check = QCheckBox(skill.capitalize())
            self.skill_checks[skill] = check
            skills_layout.addWidget(check, idx // 2, idx % 2)
        form.addRow("Compétences *:", skills_widget)
        
        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 20)
        self.capacity_input.setValue(5)
        form.addRow("Capacité/jour:", self.capacity_input)
        
        self.available_check = QCheckBox("Disponible")
        self.available_check.setChecked(True)
        form.addRow("", self.available_check)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 Enregistrer" if technician else "➕ Créer")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        # Load data if editing
        if technician:
            self.name_input.setText(technician['name'])
            for skill in technician['skills']:
                if skill in self.skill_checks:
                    self.skill_checks[skill].setChecked(True)
            self.capacity_input.setValue(technician['maxTasksPerDay'])
            self.available_check.setChecked(technician['available'])
    
    def get_data(self):
        skills = [skill for skill, check in self.skill_checks.items() if check.isChecked()]
        # Generate random coordinates around Paris for diversity
        import random
        base_lat = 48.8566
        base_lng = 2.3522
        # Add variation of +/- 0.15 degrees for technician homes
        lat_offset = (random.random() - 0.5) * 0.3
        lng_offset = (random.random() - 0.5) * 0.3
        
        return {
            'name': self.name_input.text(),
            'skills': skills,
            'maxTasksPerDay': self.capacity_input.value(),
            'available': self.available_check.isChecked(),
            'location': {
                'lat': base_lat + lat_offset,
                'lng': base_lng + lng_offset,
                'address': ''
            }
        }


class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Modifier tâche" if task else "Nouvelle tâche")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex: Réparation fuite cuisine")
        form.addRow("Titre *:", self.title_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Détails supplémentaires...")
        form.addRow("Description:", self.description_input)
        
        self.skill_combo = QComboBox()
        self.skill_combo.addItems(['plomberie', 'électricité', 'climatisation', 'chauffage', 'serrurerie', 'peinture'])
        form.addRow("Compétence requise *:", self.skill_combo)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['low', 'medium', 'high'])
        self.priority_combo.setCurrentText('medium')
        form.addRow("Priorité:", self.priority_combo)
        
        self.duration_input = QSpinBox()
        self.duration_input.setRange(15, 480)
        self.duration_input.setSingleStep(15)
        self.duration_input.setValue(60)
        self.duration_input.setSuffix(" min")
        form.addRow("Durée:", self.duration_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Ex: 15 Rue de la Pompe, Paris")
        form.addRow("Adresse *:", self.address_input)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 Enregistrer" if task else "➕ Créer")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        # Load data if editing
        if task:
            self.title_input.setText(task['title'])
            self.description_input.setPlainText(task.get('description', ''))
            self.skill_combo.setCurrentText(task['requiredSkill'])
            self.priority_combo.setCurrentText(task['priority'])
            self.duration_input.setValue(task['duration'])
            self.address_input.setText(task['location'].get('address', ''))
    
    def get_data(self):
        # Generate random coordinates around Paris for diversity
        import random
        base_lat = 48.8566
        base_lng = 2.3522
        # Add variation of +/- 0.1 degrees (roughly 10km)
        lat_offset = (random.random() - 0.5) * 0.2
        lng_offset = (random.random() - 0.5) * 0.2
        
        return {
            'title': self.title_input.text(),
            'description': self.description_input.toPlainText(),
            'requiredSkill': self.skill_combo.currentText(),
            'priority': self.priority_combo.currentText(),
            'duration': self.duration_input.value(),
            'location': {
                'lat': base_lat + lat_offset,
                'lng': base_lng + lng_offset,
                'address': self.address_input.text()
            }
        }


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
