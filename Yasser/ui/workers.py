from PyQt6.QtCore import QThread, pyqtSignal
from optimizer import ProductionOptimizer


class SolverWorker(QThread):
    finished_signal = pyqtSignal(dict)  # Signal émis à la fin avec les résultats

    def __init__(self, markets, sites, costs):
        super().__init__()
        self.markets = markets
        self.sites = sites
        self.costs = costs

    def run(self):
        # Appel de la logique métier
        optimizer = ProductionOptimizer(self.markets, self.sites, self.costs)
        results = optimizer.solve()
        self.finished_signal.emit(results)
