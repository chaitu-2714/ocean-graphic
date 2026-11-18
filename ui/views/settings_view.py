from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QLineEdit,
    QComboBox, QFormLayout, QMessageBox, QFileDialog, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from database import db_manager
from config import config

class SettingsView(QWidget):
    theme_changed_signal = Signal(str)

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        top_bar = QFrame()
        top_bar.setProperty("class", "CardFrame")
        top_layout = QHBoxLayout(top_bar)

        title = QLabel("Application Settings & User Profile")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        layout.addWidget(top_bar)

        # Splitter: Left User Profile / Right Theme & System
        main_split = QHBoxLayout()
        main_split.setSpacing(20)

        # Left Profile Card
        prof_card = QFrame()
        prof_card.setProperty("class", "CardFrame")
        prof_layout = QVBoxLayout(prof_card)

        prof_title = QLabel("User Profile Information")
        prof_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        prof_title.setStyleSheet("color: #38BDF8;")
        prof_layout.addWidget(prof_title)

        form = QFormLayout()

        self.txt_name = QLineEdit(self.current_user.get("name", "Dr. Oceanographer"))
        self.txt_email = QLineEdit(self.current_user.get("email", "admin@oceanmind.ai"))
        self.txt_email.setReadOnly(True)  # Email unique key
        self.txt_inst = QLineEdit(self.current_user.get("institution", "National Institute of Oceanography"))
        self.txt_photo = QLineEdit(self.current_user.get("photo_path", ""))

        form.addRow("Full Name:", self.txt_name)
        form.addRow("Email:", self.txt_email)
        form.addRow("Institution:", self.txt_inst)
        form.addRow("Photo Path:", self.txt_photo)

        prof_layout.addLayout(form)

        save_prof_btn = QPushButton("💾 Save Profile Changes")
        save_prof_btn.setProperty("class", "PrimaryBtn")
        save_prof_btn.clicked.connect(self._save_profile)

        prof_layout.addWidget(save_prof_btn)
        prof_layout.addStretch()

        main_split.addWidget(prof_card, stretch=1)

        # Right Theme & Config Card
        sys_card = QFrame()
        sys_card.setProperty("class", "CardFrame")
        sys_layout = QVBoxLayout(sys_card)

        sys_title = QLabel("Appearance & Theme Settings")
        sys_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sys_title.setStyleSheet("color: #38BDF8;")
        sys_layout.addWidget(sys_title)

        theme_form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Ocean Dark", "Ocean Light"])
        current_theme = db_manager.get_theme()
        self.theme_combo.setCurrentText(current_theme)

        theme_form.addRow("Active Theme:", self.theme_combo)

        sys_layout.addLayout(theme_form)

        apply_theme_btn = QPushButton("🎨 Apply Theme Choice")
        apply_theme_btn.setProperty("class", "PrimaryBtn")
        apply_theme_btn.clicked.connect(self._apply_theme)

        sys_layout.addWidget(apply_theme_btn)
        sys_layout.addSpacing(20)

        # System Paths Info
        info_title = QLabel("System Environment Info")
        info_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info_title.setStyleSheet("color: #38BDF8;")
        sys_layout.addWidget(info_title)

        sys_info = QLabel(
            f"<b>Database</b>: {config.get('db_path')}<br>"
            f"<b>ChromaDB Directory</b>: {config.get('chroma_dir')}<br>"
            f"<b>Ollama Endpoint</b>: {config.get('ollama_url')}<br>"
            f"<b>Embedding Model</b>: {config.get('embedding_model')}"
        )
        sys_info.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.5;")
        sys_layout.addWidget(sys_info)

        sys_layout.addStretch()
        main_split.addWidget(sys_card, stretch=1)

        layout.addLayout(main_split)

    def set_user(self, user_dict):
        self.current_user = user_dict
        self.txt_name.setText(user_dict.get("name", ""))
        self.txt_email.setText(user_dict.get("email", ""))
        self.txt_inst.setText(user_dict.get("institution", ""))
        self.txt_photo.setText(user_dict.get("photo_path", ""))

    def _save_profile(self):
        user_id = self.current_user.get("id", 1)
        name = self.txt_name.text().strip()
        inst = self.txt_inst.text().strip()
        photo = self.txt_photo.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Name cannot be empty.")
            return

        db_manager.update_user_profile(user_id, name, inst, photo)
        self.current_user["name"] = name
        self.current_user["institution"] = inst
        self.current_user["photo_path"] = photo

        QMessageBox.information(self, "Profile Updated", "User profile details updated successfully!")

    def _apply_theme(self):
        selected_theme = self.theme_combo.currentText()
        db_manager.set_theme(selected_theme)
        self.theme_changed_signal.emit(selected_theme)
        QMessageBox.information(self, "Theme Switch", f"Theme updated to '{selected_theme}'.")
