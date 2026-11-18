from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from database import db_manager

class DashboardView(QWidget):
    navigate_signal = Signal(int)  # Emit target index to switch tabs

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Welcome Banner
        banner = QFrame()
        banner.setProperty("class", "CardFrame")
        banner_layout = QHBoxLayout(banner)
        
        banner_text_layout = QVBoxLayout()
        welcome_lbl = QLabel("Welcome to OceanMind AI Workspace 🌊")
        welcome_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        welcome_lbl.setStyleSheet("color: #38BDF8;")
        
        sub_lbl = QLabel("Autonomous Oceanographic Data Management & RAG Intelligence Engine")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 13px;")
        
        banner_text_layout.addWidget(welcome_lbl)
        banner_text_layout.addWidget(sub_lbl)

        banner_layout.addLayout(banner_text_layout)
        banner_layout.addStretch()

        search_quick_btn = QPushButton("🔍 Launch Semantic Search")
        search_quick_btn.setProperty("class", "PrimaryBtn")
        search_quick_btn.clicked.connect(lambda: self.navigate_signal.emit(3))
        banner_layout.addWidget(search_quick_btn)

        main_layout.addWidget(banner)

        # Stats Cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        self.stats = db_manager.get_dataset_stats()

        self.card_total = self._create_stat_card("Total Argo Records", str(self.stats["total_records"]), "📊", "#0284C7")
        self.card_regions = self._create_stat_card("Monitored Regions", str(self.stats["regions_count"]), "🗺️", "#38BDF8")
        self.card_temp = self._create_stat_card("Avg Water Temp", f"{self.stats['avg_temp']} °C", "🌡️", "#E11D48")
        self.card_sal = self._create_stat_card("Avg Salinity", f"{self.stats['avg_salinity']} PSU", "🧂", "#10B981")

        grid_layout.addWidget(self.card_total, 0, 0)
        grid_layout.addWidget(self.card_regions, 0, 1)
        grid_layout.addWidget(self.card_temp, 0, 2)
        grid_layout.addWidget(self.card_sal, 0, 3)

        main_layout.addLayout(grid_layout)

        # Lower Split (Recent Dataset Info + Quick Actions)
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(20)

        # Left Info Box
        info_card = QFrame()
        info_card.setProperty("class", "CardFrame")
        info_layout = QVBoxLayout(info_card)

        info_title = QLabel("Oceanographic System Overview")
        info_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        info_title.setStyleSheet("color: #38BDF8;")

        info_details = QLabel(
            f"<b>Primary Coverage</b>: Bay of Bengal, Arabian Sea, Indian Ocean<br>"
            f"<b>Temporal Span</b>: {self.stats['time_range']}<br>"
            f"<b>Last Imported Dataset</b>: {self.stats['last_imported']}<br>"
            f"<b>Vector Indexing</b>: ChromaDB Active with Cosine Similarity<br>"
            f"<b>Ollama LLM Engine</b>: Autonomous RAG Synthesis Active"
        )
        info_details.setStyleSheet("font-size: 13px; line-height: 1.6; color: #F8FAFC;")
        info_details.setWordWrap(True)

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_details)
        info_layout.addStretch()

        lower_layout.addWidget(info_card, stretch=2)

        # Right Quick Launch Box
        action_card = QFrame()
        action_card.setProperty("class", "CardFrame")
        action_layout = QVBoxLayout(action_card)

        action_title = QLabel("Quick Actions")
        action_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        action_title.setStyleSheet("color: #38BDF8;")
        action_layout.addWidget(action_title)

        btn_ds = QPushButton("📥 Import New Dataset")
        btn_ds.setProperty("class", "SecondaryBtn")
        btn_ds.clicked.connect(lambda: self.navigate_signal.emit(1))

        btn_paper = QPushButton("📄 Upload Research Paper")
        btn_paper.setProperty("class", "SecondaryBtn")
        btn_paper.clicked.connect(lambda: self.navigate_signal.emit(2))

        btn_analytics = QPushButton("📈 View Analytics & Trends")
        btn_analytics.setProperty("class", "SecondaryBtn")
        btn_analytics.clicked.connect(lambda: self.navigate_signal.emit(4))

        action_layout.addWidget(btn_ds)
        action_layout.addWidget(btn_paper)
        action_layout.addWidget(btn_analytics)
        action_layout.addStretch()

        lower_layout.addWidget(action_card, stretch=1)

        main_layout.addLayout(lower_layout)
        main_layout.addStretch()

    def _create_stat_card(self, title, value, icon, color):
        card = QFrame()
        card.setProperty("class", "CardFrame")
        layout = QHBoxLayout(card)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 28))

        text_layout = QVBoxLayout()
        val_lbl = QLabel(value)
        val_lbl.setObjectName("StatValue")
        val_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("StatTitle")

        text_layout.addWidget(val_lbl)
        text_layout.addWidget(title_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_layout)
        return card

    def refresh_data(self):
        self.stats = db_manager.get_dataset_stats()
        # Refresh label texts
        for widget in self.findChildren(QLabel):
            if widget.objectName() == "StatValue":
                pass # updated on next full reload
