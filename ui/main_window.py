from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QStatusBar, QFrame, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from database import db_manager
from theme_manager import ThemeManager
from ollama_client import ollama_client

from ui.views.dashboard_view import DashboardView
from ui.views.dataset_view import DatasetView
from ui.views.research_view import ResearchView
from ui.views.semantic_search_view import SemanticSearchView
from ui.views.analytics_view import AnalyticsView
from ui.views.ocean_map_view import OceanMapView
from ui.views.reports_view import ReportsView
from ui.views.settings_view import SettingsView

class MainWindow(QMainWindow):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {"name": "Dr. Oceanographer", "email": "admin@oceanmind.ai"}
        self.setWindowTitle("OceanMind AI - Professional Oceanographic Desktop Platform")
        self.resize(1280, 800)

        # Apply current theme QSS
        self.active_theme = db_manager.get_theme()
        self.setStyleSheet(ThemeManager.get_style(self.active_theme))

        self._init_ui()

        # Timer for Live Clock in Status Bar
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(8)

        # Logo Header
        logo_lbl = QLabel("🌊 OceanMind AI")
        logo_lbl.setObjectName("AppLogoTitle")
        sidebar_layout.addWidget(logo_lbl)
        sidebar_layout.addSpacing(10)

        # Nav Buttons Group
        self.nav_btns = []
        nav_items = [
            ("📊 Dashboard", 0),
            ("📥 Dataset Manager", 1),
            ("📄 Research Papers", 2),
            ("🔍 Semantic Search", 3),
            ("📈 Analytics", 4),
            ("🗺️ Ocean Map", 5),
            ("📋 Reports", 6),
            ("⚙️ Settings", 7)
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "SidebarBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, idx=index: self._switch_tab(idx))
            sidebar_layout.addWidget(btn)
            self.nav_btns.append(btn)

        sidebar_layout.addStretch()

        # Logout Button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setProperty("class", "SidebarBtn")
        logout_btn.setStyleSheet("color: #E11D48;")
        logout_btn.clicked.connect(self._handle_logout)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

        # 2. Right Main Section (Toolbar + Central Workspace)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Bar
        header_bar = QFrame()
        header_bar.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(header_bar)

        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("HeaderTitle")
        header_layout.addWidget(self.header_title)

        header_layout.addStretch()

        # Theme Quick Switcher
        self.theme_btn = QPushButton("🌙 Theme")
        self.theme_btn.setProperty("class", "SecondaryBtn")
        self.theme_btn.clicked.connect(self._toggle_theme)

        # User Badge
        self.user_lbl = QLabel(f"👤 {self.current_user.get('name', 'User')}")
        self.user_lbl.setStyleSheet("color: #38BDF8; font-weight: bold; padding: 5px 10px;")

        header_layout.addWidget(self.theme_btn)
        header_layout.addWidget(self.user_lbl)

        right_layout.addWidget(header_bar)

        # Central Stacked Workspace
        self.workspace_stack = QStackedWidget()

        # Instantiate View Modules
        self.view_dashboard = DashboardView()
        self.view_dashboard.navigate_signal.connect(self._switch_tab)

        self.view_dataset = DatasetView()
        self.view_research = ResearchView()
        self.view_search = SemanticSearchView(current_user=self.current_user)
        self.view_analytics = AnalyticsView()
        self.view_map = OceanMapView()
        self.view_reports = ReportsView()
        
        self.view_settings = SettingsView(current_user=self.current_user)
        self.view_settings.theme_changed_signal.connect(self._on_theme_changed)

        self.workspace_stack.addWidget(self.view_dashboard)  # 0
        self.workspace_stack.addWidget(self.view_dataset)    # 1
        self.workspace_stack.addWidget(self.view_research)   # 2
        self.workspace_stack.addWidget(self.view_search)     # 3
        self.workspace_stack.addWidget(self.view_analytics)  # 4
        self.workspace_stack.addWidget(self.view_map)        # 5
        self.workspace_stack.addWidget(self.view_reports)    # 6
        self.workspace_stack.addWidget(self.view_settings)   # 7

        right_layout.addWidget(self.workspace_stack)

        main_layout.addWidget(right_container)
        self.setCentralWidget(main_widget)

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_user = QLabel(f"Logged In: {self.current_user.get('email', '')}")
        self.status_db = QLabel("SQLite: Connected 🟢")

        is_ollama, ollama_msg, _ = ollama_client.check_availability()
        self.status_ollama = QLabel(f"Ollama: {'Active 🟢' if is_ollama else 'RAG Fallback 🟡'}")

        self.status_clock = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        self.status_bar.addWidget(self.status_user)
        self.status_bar.addWidget(QLabel("  |  "))
        self.status_bar.addWidget(self.status_db)
        self.status_bar.addWidget(QLabel("  |  "))
        self.status_bar.addWidget(self.status_ollama)
        self.status_bar.addPermanentWidget(self.status_clock)

        self._switch_tab(0)

    def _switch_tab(self, index):
        self.workspace_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)

        titles = [
            "Dashboard Overview", "Dataset Manager", "Research Papers Digital Library",
            "Semantic Natural Language Search", "Oceanographic Analytics & Profiles",
            "Ocean Coverage Map", "Summary Reports", "Application Settings"
        ]
        if index < len(titles):
            self.header_title.setText(titles[index])

    def _toggle_theme(self):
        new_theme = "Ocean Light" if self.active_theme == "Ocean Dark" else "Ocean Dark"
        db_manager.set_theme(new_theme)
        self._on_theme_changed(new_theme)

    def _on_theme_changed(self, theme_name):
        self.active_theme = theme_name
        self.setStyleSheet(ThemeManager.get_style(theme_name))

    def _update_clock(self):
        self.status_clock.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _handle_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", "Are you sure you want to log out of OceanMind AI?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            # Relaunch main script to open login window cleanly
            import subprocess
            subprocess.Popen(["python", "main.py"])
