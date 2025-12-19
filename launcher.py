# launcher.py
"""
🚀 Lanceur Principal - Projet RO
Interface pour lancer les applications de chaque membre du groupe
"""

import sys
import subprocess
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QFont, QIcon


class ApplicationLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Projet RO - Lanceur d'Applications")
        self.setGeometry(200, 200, 800, 500)
        
        # Chemin racine du projet
        self.project_root = Path(__file__).parent
        
        # Processus en cours
        self.processes = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre
        title = QLabel("🏥 Projet Recherche Opérationnelle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Problème de Localisation et Allocation d'Hôpitaux")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Configuration des applications
        apps = [
            {
                "name": "Youssef Chékili",
                "icon": "👨‍💻",
                "description": "Problème 4 - Application 2",
                "folder": "Youssef",
                "file": "gui_simple.py",
                "color": "#4CAF50"
            },
            {
                "name": "Dhia Selmi",
                "icon": "👨‍🔬",
                "description": "Problème 4 - Application 1",
                "folder": "Dhia",
                "file": "problem_1.py",
                "color": "#2196F3"
            },
            {
                "name": "Yasser Chouket",
                "icon": "👨‍💼",
                "description": "Problème 4 - Application 3",
                "folder": "Yasser",
                "file": "main.py",
                "color": "#FF9800"
            },
            {
                "name": "Yassine Kolsi",
                "icon": "👨‍🎓",
                "description": "Problème 2 - Application 3",
                "folder": "Kolsi/src",
                "file": "main.py",
                "color": "#9C27B0"
            },
            {
                "name": "Youssef Gargouri",
                "icon": "🚀",
                "description": "Routage Personnel - Maintenance",
                "folder": "Doj",
                "file": "start_app.ps1",
                "color": "#E91E63   ",
            }
        ]
        
        # Créer les boutons
        for app in apps:
            app_widget = self.create_app_button(app)
            layout.addWidget(app_widget)
        
        layout.addStretch()
        
        # Bouton fermer tout
        close_all_btn = QPushButton("❌ Fermer Toutes les Applications")
        close_all_btn.setMinimumHeight(40)
        close_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        close_all_btn.clicked.connect(self.close_all_apps)
        layout.addWidget(close_all_btn)
    
    def create_app_button(self, app_info):
        """Crée un widget bouton pour une application"""
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bouton principal
        btn = QPushButton(f"{app_info['icon']}  {app_info['name']}")
        btn.setMinimumHeight(80)
        btn.setMinimumWidth(200)
        
        btn_style = f"""
            QPushButton {{
                background-color: {app_info['color']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(app_info['color'])};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(app_info['color'], 0.3)};
            }}
        """
        btn.setStyleSheet(btn_style)
        if app_info.get('needs_backend', False):
            btn.clicked.connect(lambda checked=False, info=app_info: self.launch_app_with_backend(info))
        else:
            btn.clicked.connect(lambda checked=False, info=app_info: self.launch_app(info))
        
        container_layout.addWidget(btn)
        
        # Description
        desc_label = QLabel(app_info['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 12px; color: #555;")
        container_layout.addWidget(desc_label, stretch=1)
        
        return container
    
    def darken_color(self, hex_color, factor=0.15):
        """Assombrit une couleur hexadécimale"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def launch_app(self, app_info):
        """Lance une application"""
        app_name = app_info['name']
        
        # Cas spécial : Application avec backend
        if app_info.get('needs_backend', False):
            self.launch_app_with_backend(app_info)
            return
        
        folder = self.project_root / app_info['folder']
        file_path = folder / app_info['file']
        
        # Vérifier que le fichier existe
        if not file_path.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Le fichier {app_info['file']} n'existe pas dans {folder}"
            )
            return
        
        # Vérifier si l'application est déjà lancée
        if app_name in self.processes and self.processes[app_name].state() == QProcess.Running:
            reply = QMessageBox.question(
                self,
                "Application Déjà Lancée",
                f"L'application {app_name} est déjà en cours d'exécution.\nVoulez-vous la relancer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.processes[app_name].kill()
                self.processes[app_name].waitForFinished()
            else:
                return
        
        # Créer le processus
        process = QProcess(self)
        process.setWorkingDirectory(str(folder))
        
        # Connecter les signaux pour le suivi
        process.started.connect(lambda: self.on_app_started(app_name))
        process.finished.connect(lambda exit_code, exit_status: self.on_app_finished(app_name, exit_code))
        process.errorOccurred.connect(lambda error: self.on_app_error(app_name, error))
        
        # Lancer le processus
        if app_info['file'].endswith('.ps1'):
            process.start("powershell", ["-ExecutionPolicy", "Bypass", "-File", app_info['file']])
        else:
            python_exe = sys.executable
            process.start(python_exe, [app_info['file']])
        
        self.processes[app_name] = process
    
    def launch_app_with_backend(self, app_info):
        """Lance une application avec son backend d'abord"""
        app_name = app_info['name']
        backend_name = f"{app_name} (Backend)"
        ui_name = f"{app_name} (UI)"
        
        # Vérifier si déjà lancé
        if backend_name in self.processes and self.processes[backend_name].state() == QProcess.Running:
            reply = QMessageBox.question(
                self,
                "Application Déjà Lancée",
                f"L'application {app_name} est déjà en cours d'exécution.\nVoulez-vous la relancer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Fermer backend et UI
                if backend_name in self.processes:
                    self.processes[backend_name].kill()
                    self.processes[backend_name].waitForFinished()
                if ui_name in self.processes:
                    self.processes[ui_name].kill()
                    self.processes[ui_name].waitForFinished()
            else:
                return
        
        # 1. Lancer le Backend
        backend_folder = self.project_root / app_info['folder'] / "backend"
        backend_file = backend_folder / "main.py"
        
        if not backend_file.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Le fichier backend/main.py n'existe pas dans {app_info['folder']}"
            )
            return
        
        backend_process = QProcess(self)
        backend_process.setWorkingDirectory(str(backend_folder))
        backend_process.started.connect(lambda: self.on_backend_started(app_name))
        backend_process.errorOccurred.connect(lambda error: self.on_app_error(backend_name, error))
        
        python_exe = sys.executable
        backend_process.start(python_exe, ["main.py"])
        
        self.processes[backend_name] = backend_process
        
        # 2. Attendre 2 secondes puis lancer l'UI
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.launch_ui_after_backend(app_info, ui_name))
    
    def on_backend_started(self, app_name):
        """Callback quand le backend démarre"""
        QMessageBox.information(
            self,
            "Backend Lancé",
            f"✅ Backend de {app_name} démarré!\n\nL'interface va se lancer dans 2 secondes..."
        )
    
    def launch_ui_after_backend(self, app_info, ui_name):
        """Lance l'UI après que le backend ait démarré"""
        ui_folder = self.project_root / app_info['folder'] / "ui"
        ui_file = ui_folder / app_info['file']
        
        if not ui_file.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Le fichier {app_info['file']} n'existe pas dans {ui_folder}"
            )
            return
        
        ui_process = QProcess(self)
        ui_process.setWorkingDirectory(str(ui_folder))
        ui_process.started.connect(lambda: self.on_ui_started(app_info['name']))
        ui_process.finished.connect(lambda exit_code, exit_status: self.on_app_finished(ui_name, exit_code))
        ui_process.errorOccurred.connect(lambda error: self.on_app_error(ui_name, error))
        
        python_exe = sys.executable
        ui_process.start(python_exe, [app_info['file']])
        
        self.processes[ui_name] = ui_process
    
    def on_ui_started(self, app_name):
        """Callback quand l'UI démarre"""
        QMessageBox.information(
            self,
            "Interface Lancée",
            f"✅ Interface de {app_name} lancée avec succès!\n\nL'application est maintenant prête."
        )
    
    def on_app_started(self, app_name):
        """Callback quand une application démarre"""
        QMessageBox.information(
            self,
            "Application Lancée",
            f"✅ {app_name} a été lancé avec succès!\n\nLa fenêtre devrait apparaître dans quelques instants."
        )
    
    def on_app_finished(self, app_name, exit_code):
        """Callback quand une application se termine"""
        if exit_code != 0:
            QMessageBox.warning(
                self,
                "Application Terminée",
                f"⚠️ {app_name} s'est terminé avec le code: {exit_code}"
            )
    
    def on_app_error(self, app_name, error):
        """Callback en cas d'erreur"""
        error_messages = {
            QProcess.FailedToStart: "Échec du démarrage. Vérifiez que Python est installé.",
            QProcess.Crashed: "L'application a planté.",
            QProcess.Timedout: "Timeout lors du lancement.",
            QProcess.WriteError: "Erreur d'écriture.",
            QProcess.ReadError: "Erreur de lecture.",
            QProcess.UnknownError: "Erreur inconnue."
        }
        
        QMessageBox.critical(
            self,
            "Erreur",
            f"❌ Erreur lors du lancement de {app_name}:\n{error_messages.get(error, 'Erreur inconnue')}"
        )
    
    def close_all_apps(self):
        """Ferme toutes les applications en cours"""
        running_apps = [name for name, proc in self.processes.items() 
                       if proc.state() == QProcess.Running]
        
        if not running_apps:
            QMessageBox.information(self, "Info", "Aucune application en cours d'exécution.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous fermer les applications suivantes ?\n\n" + "\n".join(f"• {app}" for app in running_apps),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for name, process in self.processes.items():
                if process.state() == QProcess.Running:
                    process.kill()
                    process.waitForFinished()
            
            QMessageBox.information(self, "Succès", f"✅ {len(running_apps)} application(s) fermée(s).")
    
    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre principale"""
        running_apps = [name for name, proc in self.processes.items() 
                       if proc.state() == QProcess.Running]
        
        if running_apps:
            reply = QMessageBox.question(
                self,
                "Confirmation de Fermeture",
                f"Des applications sont encore en cours :\n\n" + "\n".join(f"• {app}" for app in running_apps) +
                "\n\nVoulez-vous les fermer et quitter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                for process in self.processes.values():
                    if process.state() == QProcess.Running:
                        process.kill()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Style global
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
    """)
    
    launcher = ApplicationLauncher()
    launcher.show()
    
    sys.exit(app.exec())
