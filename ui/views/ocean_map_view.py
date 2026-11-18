import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import db_manager

class OceanMapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        top_bar = QFrame()
        top_bar.setProperty("class", "CardFrame")
        top_layout = QHBoxLayout(top_bar)

        title = QLabel("Oceanographic Regional Coordinates & Coverage Map")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        layout.addWidget(top_bar)

        # Map Frame
        map_card = QFrame()
        map_card.setProperty("class", "CardFrame")
        map_layout = QVBoxLayout(map_card)

        self.canvas = MapCanvas()
        map_layout.addWidget(self.canvas)

        layout.addWidget(map_card)

        # Refresh map with records
        datasets = db_manager.search_datasets(limit=500)
        self.canvas.plot_map(datasets)

class MapCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(9, 5), facecolor='#1E293B')
        super().__init__(fig)
        self.setParent(parent)

    def plot_map(self, datasets):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#0F172A')

        if datasets:
            lats = [d['latitude'] for d in datasets]
            lons = [d['longitude'] for d in datasets]
            temps = [d['temperature'] for d in datasets]

            sc = ax.scatter(lons, lats, c=temps, cmap='plasma', s=40, alpha=0.8, edgecolors='none')
            cbar = self.figure.colorbar(sc, ax=ax)
            cbar.set_label('Temperature (°C)', color='#F8FAFC')
            cbar.ax.yaxis.set_tick_params(color='#F8FAFC')
            plt_ticks = cbar.ax.get_yticklabels()
            for t in plt_ticks:
                t.set_color('#F8FAFC')

            ax.set_title('Argo Float Observation Locations (Bay of Bengal & Indian Ocean)', color='#F8FAFC', fontsize=12, fontweight='bold')
            ax.set_xlabel('Longitude (°E)', color='#94A3B8')
            ax.set_ylabel('Latitude (°N)', color='#94A3B8')
            ax.grid(True, color='#334155', linestyle='--', alpha=0.5)
            ax.tick_params(colors='#94A3B8')

            # Draw geographical reference box for Bay of Bengal
            ax.axvspan(80, 95, color='#0284C7', alpha=0.08, label='Bay of Bengal Basin')
        else:
            ax.text(0.5, 0.5, 'No coordinates to plot', color='#94A3B8', ha='center', va='center')

        self.figure.tight_layout()
        self.draw()
