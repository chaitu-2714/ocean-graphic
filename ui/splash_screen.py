import sys
import time
from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPainterPath

from config import config
from database import db_manager
from vector_store import vector_store
from ollama_client import ollama_client
from theme_manager import ThemeManager

class OceanMindSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(540, 340)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.progress_value = 0
        self.current_step = 0

        self.steps = [
            ("Initializing UI Components...", 15),
            ("Loading Configuration (.env, config.json)...", 30),
            ("Checking SQLite Database...", 50),
            ("Checking ChromaDB Vector Store...", 70),
            ("Checking Ollama Service...", 85),
            ("Loading Theme & Resources...", 95),
            ("Ready!", 100)
        ]

        self._draw_splash()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_step)

    def start_loading(self):
        self.show()
        QApplication.processEvents()
        self.timer.start(250)

    def _draw_splash(self, status_msg="Initializing OceanMind AI...", progress=0):
        pixmap = QPixmap(540, 340)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background Card Gradient
        gradient = QLinearGradient(0, 0, 540, 340)
        gradient.setColorAt(0.0, QColor("#0F172A"))
        gradient.setColorAt(1.0, QColor("#1E293B"))

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, 540, 340), 16, 16)
        painter.fillPath(path, gradient)

        # Border
        painter.setPen(QColor("#38BDF8"))
        painter.drawPath(path)

        # Logo Wave Icon
        painter.setBrush(QColor("#0284C7"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(230, 45, 80, 80)

        painter.setPen(QColor("#FFFFFF"))
        font_logo = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(font_logo)
        painter.drawText(230, 45, 80, 80, Qt.AlignCenter, "🌊")

        # Title
        painter.setPen(QColor("#38BDF8"))
        font_title = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font_title)
        painter.drawText(0, 140, 540, 40, Qt.AlignCenter, "OceanMind AI")

        # Subtitle
        painter.setPen(QColor("#94A3B8"))
        font_sub = QFont("Segoe UI", 11)
        painter.setFont(font_sub)
        painter.drawText(0, 180, 540, 25, Qt.AlignCenter, "Autonomous Oceanographic Intelligence & RAG Platform")

        # Progress Bar Outer Frame
        bar_x, bar_y, bar_w, bar_h = 60, 230, 420, 12
        painter.setBrush(QColor("#334155"))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 6, 6)

        # Progress Bar Fill
        if progress > 0:
            fill_w = int(bar_w * (progress / 100.0))
            fill_gradient = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            fill_gradient.setColorAt(0.0, QColor("#0284C7"))
            fill_gradient.setColorAt(1.0, QColor("#38BDF8"))
            painter.setBrush(fill_gradient)
            painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 6, 6)

        # Status Message Text
        painter.setPen(QColor("#CBD5E1"))
        font_status = QFont("Segoe UI", 10)
        painter.setFont(font_status)
        painter.drawText(0, 260, 540, 25, Qt.AlignCenter, status_msg)

        painter.end()
        self.setPixmap(pixmap)

    def _next_step(self):
        if self.current_step < len(self.steps):
            msg, prog = self.steps[self.current_step]
            self._draw_splash(msg, prog)
            
            # Execute actual check for each step
            if self.current_step == 2: # DB Check
                try:
                    db_manager.get_theme()
                except Exception as e:
                    self._show_error("Database Initialization Error", str(e))

            elif self.current_step == 3: # ChromaDB Check
                if vector_store.paper_collection is None:
                    print("ChromaDB in-memory fallback active.")

            elif self.current_step == 4: # Ollama Check
                is_online, status_str, _ = ollama_client.check_availability()
                print(f"Ollama Startup Check: {status_str}")

            self.current_step += 1
        else:
            self.timer.stop()
            self.finish_loading()

    def finish_loading(self):
        self.close()

    def _show_error(self, title, message):
        self.timer.stop()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"Critical Component Failure:\n{message}")
        msg_box.exec()
