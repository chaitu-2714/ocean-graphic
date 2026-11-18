import sys
import re
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QMessageBox, QFrame, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap

from database import db_manager
from theme_manager import ThemeManager

class LoginWindow(QDialog):
    login_success_signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OceanMind AI - Authentication")
        self.setFixedSize(500, 620)
        self.setStyleSheet(ThemeManager.get_style(db_manager.get_theme()))

        self.current_user = None

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header Logo & Title
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)

        logo_lbl = QLabel("🌊")
        logo_lbl.setFont(QFont("Segoe UI", 36))
        logo_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel("OceanMind AI")
        title_lbl.setObjectName("AppLogoTitle")
        title_lbl.setAlignment(Qt.AlignCenter)

        sub_lbl = QLabel("Professional Oceanographic Intelligence Platform")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        sub_lbl.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(logo_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(sub_lbl)

        main_layout.addWidget(header_frame)

        # Stacked Widget (0: Login, 1: Register, 2: Forgot Password)
        self.stack = QStackedWidget()
        
        self.stack.addWidget(self._create_login_widget())
        self.stack.addWidget(self._create_register_widget())
        self.stack.addWidget(self._create_forgot_password_widget())

        main_layout.addWidget(self.stack)

    # --- Login Form ---
    def _create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        form_card = QFrame()
        form_card.setProperty("class", "CardFrame")
        form_layout = QVBoxLayout(form_card)

        form_title = QLabel("User Sign In")
        form_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        form_title.setStyleSheet("color: #38BDF8;")
        form_layout.addWidget(form_title)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email (e.g. admin@oceanmind.ai)")
        self.login_email.setText("admin@oceanmind.ai")  # Pre-filled demo user

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setText("admin123")  # Pre-filled demo pass

        form_layout.addWidget(QLabel("Email Address"))
        form_layout.addWidget(self.login_email)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.login_password)

        login_btn = QPushButton("Sign In")
        login_btn.setProperty("class", "PrimaryBtn")
        login_btn.clicked.connect(self._handle_login)

        form_layout.addWidget(login_btn)

        layout.addWidget(form_card)

        # Links
        links_layout = QHBoxLayout()
        reg_link = QPushButton("Create an Account")
        reg_link.setStyleSheet("color: #38BDF8; border: none; background: transparent; text-decoration: underline;")
        reg_link.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        forgot_link = QPushButton("Forgot Password?")
        forgot_link.setStyleSheet("color: #94A3B8; border: none; background: transparent; text-decoration: underline;")
        forgot_link.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        links_layout.addWidget(reg_link)
        links_layout.addStretch()
        links_layout.addWidget(forgot_link)

        layout.addLayout(links_layout)

        return widget

    # --- Registration Form ---
    def _create_register_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        form_card = QFrame()
        form_card.setProperty("class", "CardFrame")
        form_layout = QVBoxLayout(form_card)

        form_title = QLabel("Create Account")
        form_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        form_title.setStyleSheet("color: #38BDF8;")
        form_layout.addWidget(form_title)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Full Name")

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email Address")

        self.reg_institution = QLineEdit()
        self.reg_institution.setPlaceholderText("Institution / University (e.g. NIO)")

        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Password (min 6 chars)")
        self.reg_pass.setEchoMode(QLineEdit.Password)

        self.reg_confirm_pass = QLineEdit()
        self.reg_confirm_pass.setPlaceholderText("Confirm Password")
        self.reg_confirm_pass.setEchoMode(QLineEdit.Password)

        self.reg_sec_combo = QComboBox()
        self.reg_sec_combo.addItems([
            "What is your favorite ocean?",
            "What was your first oceanographic research float ID?",
            "What city was your university located in?"
        ])

        self.reg_sec_ans = QLineEdit()
        self.reg_sec_ans.setPlaceholderText("Security Recovery Answer")

        form_layout.addWidget(QLabel("Full Name"))
        form_layout.addWidget(self.reg_name)
        form_layout.addWidget(QLabel("Email"))
        form_layout.addWidget(self.reg_email)
        form_layout.addWidget(QLabel("Institution"))
        form_layout.addWidget(self.reg_institution)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.reg_pass)
        form_layout.addWidget(QLabel("Confirm Password"))
        form_layout.addWidget(self.reg_confirm_pass)
        form_layout.addWidget(QLabel("Security Question"))
        form_layout.addWidget(self.reg_sec_combo)
        form_layout.addWidget(self.reg_sec_ans)

        register_btn = QPushButton("Register & Sign In")
        register_btn.setProperty("class", "PrimaryBtn")
        register_btn.clicked.connect(self._handle_registration)

        form_layout.addWidget(register_btn)

        layout.addWidget(form_card)

        back_btn = QPushButton("← Back to Login")
        back_btn.setStyleSheet("color: #94A3B8; border: none; background: transparent;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_btn)

        return widget

    # --- Forgot Password Form ---
    def _create_forgot_password_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form_card = QFrame()
        form_card.setProperty("class", "CardFrame")
        form_layout = QVBoxLayout(form_card)

        form_title = QLabel("Password Recovery")
        form_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        form_title.setStyleSheet("color: #38BDF8;")
        form_layout.addWidget(form_title)

        self.rec_email = QLineEdit()
        self.rec_email.setPlaceholderText("Registered Email Address")

        self.rec_answer = QLineEdit()
        self.rec_answer.setPlaceholderText("Security Question Answer")

        self.rec_new_pass = QLineEdit()
        self.rec_new_pass.setPlaceholderText("New Password")
        self.rec_new_pass.setEchoMode(QLineEdit.Password)

        form_layout.addWidget(QLabel("Account Email"))
        form_layout.addWidget(self.rec_email)
        form_layout.addWidget(QLabel("Security Answer"))
        form_layout.addWidget(self.rec_answer)
        form_layout.addWidget(QLabel("New Password"))
        form_layout.addWidget(self.rec_new_pass)

        reset_btn = QPushButton("Reset Password")
        reset_btn.setProperty("class", "PrimaryBtn")
        reset_btn.clicked.connect(self._handle_password_reset)

        form_layout.addWidget(reset_btn)

        layout.addWidget(form_card)

        back_btn = QPushButton("← Back to Login")
        back_btn.setStyleSheet("color: #94A3B8; border: none; background: transparent;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_btn)

        return widget

    # --- Actions ---
    def _handle_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Validation Error", "Please enter both email and password.")
            return

        success, msg, user_dict = db_manager.authenticate_user(email, password)
        if success:
            self.current_user = user_dict
            self.login_success_signal.emit(user_dict)
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", msg)

    def _handle_registration(self):
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        institution = self.reg_institution.text().strip()
        password = self.reg_pass.text().strip()
        confirm_pass = self.reg_confirm_pass.text().strip()
        sec_q = self.reg_sec_combo.currentText()
        sec_a = self.reg_sec_ans.text().strip()

        if not name or not email or not password or not confirm_pass or not sec_a:
            QMessageBox.warning(self, "Validation Error", "Please fill in all required registration fields.")
            return

        # Email Regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters long.")
            return

        if password != confirm_pass:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return

        success, msg = db_manager.register_user(
            name=name,
            email=email,
            password=password,
            institution=institution,
            recovery_question=sec_q,
            recovery_answer=sec_a
        )

        if success:
            QMessageBox.information(self, "Success", "Registration successful! You may now sign in.")
            self.login_email.setText(email)
            self.login_password.setText(password)
            self.stack.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Registration Error", msg)

    def _handle_password_reset(self):
        email = self.rec_email.text().strip()
        answer = self.rec_answer.text().strip()
        new_pass = self.rec_new_pass.text().strip()

        if not email or not answer or not new_pass:
            QMessageBox.warning(self, "Validation Error", "Please complete all password recovery fields.")
            return

        if len(new_pass) < 6:
            QMessageBox.warning(self, "Validation Error", "New password must be at least 6 characters long.")
            return

        success, msg = db_manager.reset_password(email, answer, new_pass)
        if success:
            QMessageBox.information(self, "Password Updated", "Your password has been reset. You can now log in.")
            self.login_email.setText(email)
            self.login_password.setText(new_pass)
            self.stack.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Reset Error", msg)
