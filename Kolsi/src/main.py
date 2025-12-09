import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

# Ensure you have installed:
# pip install gurobipy PyQt6 networkx matplotlib

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set a global style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()