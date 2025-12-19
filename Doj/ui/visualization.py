import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QLabel
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath

class RouteVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.layout.addWidget(self.view)
        
        self.colors = [
            QColor("#e6194b"), QColor("#3cb44b"), QColor("#ffe119"), QColor("#4363d8"),
            QColor("#f58231"), QColor("#911eb4"), QColor("#46f0f0"), QColor("#f032e6"),
            QColor("#bcf60c"), QColor("#fabebe"), QColor("#008080"), QColor("#e6beff"),
            QColor("#9a6324"), QColor("#fffac8"), QColor("#800000"), QColor("#aaffc3")
        ]
        
        # Show placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        self.scene.clear()
        text = self.scene.addText("Aucune route optimisée à afficher\n\nCliquez sur 'Optimiser les tournées' pour générer les routes")
        text.setFont(QFont("Arial", 12))
        text.setDefaultTextColor(QColor("#666"))
        self.scene.setSceneRect(text.boundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def update_routes(self, routes, technicians):
        """Update the visualization with optimized routes"""
        print(f"[Visualizer] Updating with {len(routes)} routes and {len(technicians)} technicians")
        
        self.scene.clear()
        
        if not routes or len(routes) == 0:
            self.show_placeholder()
            return
        
        # Create tech mapping
        tech_map = {t['id']: t for t in technicians}
        
        # Collect all coordinates
        all_points = []
        
        for route in routes:
            tech_id = route.get('technicianId')
            if tech_id and tech_id in tech_map:
                tech = tech_map[tech_id]
                loc = tech.get('location', {})
                if loc.get('lat') and loc.get('lng'):
                    all_points.append((loc['lat'], loc['lng']))
            
            tasks = route.get('tasks', [])
            for task in tasks:
                loc = task.get('location', {})
                if loc.get('lat') and loc.get('lng'):
                    all_points.append((loc['lat'], loc['lng']))
        
        if not all_points:
            print("[Visualizer] No valid points found")
            self.show_placeholder()
            return
        
        print(f"[Visualizer] Found {len(all_points)} points to draw")
        
        # Calculate bounds
        lats = [p[0] for p in all_points]
        lngs = [p[1] for p in all_points]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        # Add padding (10% on each side)
        lat_range = max(max_lat - min_lat, 0.01)
        lng_range = max(max_lng - min_lng, 0.01)
        
        padding_lat = lat_range * 0.15
        padding_lng = lng_range * 0.15
        
        min_lat -= padding_lat
        max_lat += padding_lat
        min_lng -= padding_lng
        max_lng += padding_lng
        
        # Canvas dimensions
        canvas_width = 1000
        canvas_height = 700
        margin = 60
        
        # Coordinate transformation
        def to_canvas(lat, lng):
            if max_lng == min_lng:
                x = canvas_width / 2
            else:
                x = margin + (lng - min_lng) / (max_lng - min_lng) * (canvas_width - 2 * margin)
            
            if max_lat == min_lat:
                y = canvas_height / 2
            else:
                # Flip Y axis (screen coords go down)
                y = canvas_height - margin - (lat - min_lat) / (max_lat - min_lat) * (canvas_height - 2 * margin)
            
            return x, y
        
        # Set scene rect
        self.scene.setSceneRect(0, 0, canvas_width, canvas_height)
        
        # Draw each route
        for route_idx, route in enumerate(routes):
            color = self.colors[route_idx % len(self.colors)]
            
            tech_id = route.get('technicianId')
            if not tech_id or tech_id not in tech_map:
                continue
            
            tech = tech_map[tech_id]
            tech_loc = tech.get('location', {})
            
            if not tech_loc.get('lat') or not tech_loc.get('lng'):
                continue
            
            # Get starting position
            curr_x, curr_y = to_canvas(tech_loc['lat'], tech_loc['lng'])
            
            # Draw technician base as a square
            square_size = 14
            square = self.scene.addRect(
                curr_x - square_size/2, curr_y - square_size/2,
                square_size, square_size,
                QPen(color, 2),
                QBrush(color)
            )
            
            # Technician label
            tech_label = self.scene.addText(tech.get('name', 'Tech'))
            tech_label.setDefaultTextColor(color)
            tech_label.setFont(QFont("Arial", 10, QFont.Bold))
            tech_label.setPos(curr_x + 10, curr_y - 20)
            
            # Draw path through tasks
            tasks = route.get('tasks', [])
            for task_idx, task in enumerate(tasks, 1):
                task_loc = task.get('location', {})
                
                if not task_loc.get('lat') or not task_loc.get('lng'):
                    continue
                
                next_x, next_y = to_canvas(task_loc['lat'], task_loc['lng'])
                
                # Draw connecting line
                line = self.scene.addLine(curr_x, curr_y, next_x, next_y, QPen(color, 3))
                
                # Draw task point as circle
                circle_radius = 8
                circle = self.scene.addEllipse(
                    next_x - circle_radius, next_y - circle_radius,
                    circle_radius * 2, circle_radius * 2,
                    QPen(color, 2),
                    QBrush(QColor("white"))
                )
                
                # Task number label
                task_num = self.scene.addText(str(task_idx))
                task_num.setDefaultTextColor(color)
                task_num.setFont(QFont("Arial", 9, QFont.Bold))
                task_num.setPos(next_x - 4, next_y - 8)
                
                # Move to next position
                curr_x, curr_y = next_x, next_y
        
        # Fit view to scene
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.centerOn(canvas_width / 2, canvas_height / 2)
        
        print(f"[Visualizer] Drawing complete")
