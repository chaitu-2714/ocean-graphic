import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import db_manager

class AnalyticsView(QWidget):
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

        title = QLabel("Oceanographic Data Analytics & Profiles")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        self.region_combo = QComboBox()
        self.region_combo.addItems(["All Regions", "Bay of Bengal", "Arabian Sea", "Equatorial Indian Ocean", "Andaman Sea"])
        self.region_combo.currentTextChanged.connect(self.refresh_charts)

        top_layout.addWidget(QLabel("Target Region:"))
        top_layout.addWidget(self.region_combo)

        layout.addWidget(top_bar)

        # Chart Frame
        chart_card = QFrame()
        chart_card.setProperty("class", "CardFrame")
        chart_layout = QVBoxLayout(chart_card)

        self.canvas = AnalyticsCanvas()
        chart_layout.addWidget(self.canvas)

        layout.addWidget(chart_card)
        self.refresh_charts()

    def refresh_charts(self):
        region = self.region_combo.currentText()
        datasets = db_manager.search_datasets(region=region, limit=300)
        self.canvas.plot_analytics(datasets, region)

class AnalyticsCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(9, 5), facecolor='#1E293B')
        super().__init__(fig)
        self.setParent(parent)

    def plot_analytics(self, datasets, region):
        self.figure.clear()

        ax1 = self.figure.add_subplot(221, facecolor='#0F172A')
        ax2 = self.figure.add_subplot(222, facecolor='#0F172A')
        ax3 = self.figure.add_subplot(223, facecolor='#0F172A')
        ax4 = self.figure.add_subplot(224, facecolor='#0F172A')

        if datasets:
            depths = [d['depth'] for d in datasets]
            temps = [d['temperature'] for d in datasets]
            salinities = [d['salinity'] for d in datasets]
            oxys = [d['dissolved_oxygen'] for d in datasets]

            # 1. Temp vs Depth
            ax1.scatter(temps, depths, color='#38BDF8', alpha=0.6, s=15)
            ax1.invert_yaxis()
            ax1.set_title(f'Temp vs Depth ({region})', color='#F8FAFC', fontsize=10)
            ax1.set_xlabel('Temp (°C)', color='#94A3B8')
            ax1.set_ylabel('Depth (m)', color='#94A3B8')
            ax1.tick_params(colors='#94A3B8')

            # 2. Salinity vs Depth
            ax2.scatter(salinities, depths, color='#10B981', alpha=0.6, s=15)
            ax2.invert_yaxis()
            ax2.set_title(f'Salinity vs Depth ({region})', color='#F8FAFC', fontsize=10)
            ax2.set_xlabel('Salinity (PSU)', color='#94A3B8')
            ax2.set_ylabel('Depth (m)', color='#94A3B8')
            ax2.tick_params(colors='#94A3B8')

            # 3. Dissolved Oxygen vs Depth
            ax3.scatter(oxys, depths, color='#F59E0B', alpha=0.6, s=15)
            ax3.invert_yaxis()
            ax3.set_title('Dissolved Oxygen Profile', color='#F8FAFC', fontsize=10)
            ax3.set_xlabel('Oxygen (µmol/kg)', color='#94A3B8')
            ax3.set_ylabel('Depth (m)', color='#94A3B8')
            ax3.tick_params(colors='#94A3B8')

            # 4. Temp vs Salinity (T-S Diagram)
            ax4.scatter(salinities, temps, color='#EC4899', alpha=0.6, s=15)
            ax4.set_title('T-S Water Mass Diagram', color='#F8FAFC', fontsize=10)
            ax4.set_xlabel('Salinity (PSU)', color='#94A3B8')
            ax4.set_ylabel('Temp (°C)', color='#94A3B8')
            ax4.tick_params(colors='#94A3B8')

        else:
            for ax in [ax1, ax2, ax3, ax4]:
                ax.text(0.5, 0.5, 'No Data', color='#94A3B8', ha='center', va='center')

        self.figure.tight_layout()
        self.draw()
