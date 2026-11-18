import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.splash_screen import OceanMindSplashScreen
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    # Enable high-DPI scaling for crisp desktop rendering
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("OceanMind AI")
    app.setOrganizationName("OceanMind Intelligence")

    # 1. Splash Screen Sequence
    splash = OceanMindSplashScreen()
    splash.start_loading()

    # Wait for splash sequence to finish
    while splash.isVisible():
        app.processEvents()

    # 2. Open Login Window
    login_win = LoginWindow()
    main_win = None

    def on_login_success(user_dict):
        nonlocal main_win
        main_win = MainWindow(current_user=user_dict)
        main_win.show()

    login_win.login_success_signal.connect(on_login_success)

    if login_win.exec() == LoginWindow.Accepted and main_win:
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
