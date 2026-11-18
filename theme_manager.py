class ThemeManager:
    @staticmethod
    def get_style(theme_name="Ocean Dark"):
        if theme_name == "Ocean Light":
            return ThemeManager._ocean_light_qss()
        return ThemeManager._ocean_dark_qss()

    @staticmethod
    def _ocean_dark_qss():
        return """
        /* Main Window & Core Colors */
        QMainWindow, QDialog {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }

        QWidget {
            color: #F8FAFC;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }

        /* Sidebar Styling */
        #SidebarContainer {
            background-color: #1E293B;
            border-right: 1px solid #334155;
            min-width: 230px;
            max-width: 230px;
        }

        #AppLogoTitle {
            font-size: 18px;
            font-weight: bold;
            color: #38BDF8;
            padding: 10px;
        }

        QPushButton.SidebarBtn {
            background-color: transparent;
            color: #94A3B8;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
        }

        QPushButton.SidebarBtn:hover {
            background-color: #334155;
            color: #F8FAFC;
        }

        QPushButton.SidebarBtn:checked, QPushButton.SidebarBtn.active {
            background-color: #0284C7;
            color: #FFFFFF;
            font-weight: bold;
        }

        QPushButton.SidebarBtn:disabled {
            color: #475569;
            background-color: transparent;
        }

        /* Top Toolbar & Header */
        #HeaderBar {
            background-color: #1E293B;
            border-bottom: 1px solid #334155;
            min-height: 55px;
            max-height: 55px;
            padding: 0 15px;
        }

        #HeaderTitle {
            font-size: 18px;
            font-weight: 600;
            color: #F8FAFC;
        }

        /* Cards & Group Boxes */
        QFrame.CardFrame, QGroupBox {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px;
        }

        QGroupBox::title {
            color: #38BDF8;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            font-weight: bold;
        }

        /* Input Controls */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
            background-color: #0F172A;
            color: #F8FAFC;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }

        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #38BDF8;
        }

        QComboBox::drop-down {
            border: none;
            width: 24px;
        }

        /* Buttons */
        QPushButton.PrimaryBtn {
            background-color: #0284C7;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-weight: 600;
            font-size: 13px;
        }

        QPushButton.PrimaryBtn:hover {
            background-color: #0369A1;
        }

        QPushButton.SecondaryBtn {
            background-color: #334155;
            color: #F8FAFC;
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-weight: 500;
        }

        QPushButton.SecondaryBtn:hover {
            background-color: #475569;
        }

        QPushButton.DangerBtn {
            background-color: #DC2626;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-weight: 600;
        }

        QPushButton.DangerBtn:hover {
            background-color: #B91C1C;
        }

        /* Tables */
        QTableWidget, QTableView {
            background-color: #0F172A;
            color: #F8FAFC;
            gridline-color: #334155;
            border: 1px solid #334155;
            border-radius: 8px;
            selection-background-color: #0284C7;
            selection-color: #FFFFFF;
        }

        QHeaderView::section {
            background-color: #1E293B;
            color: #38BDF8;
            font-weight: bold;
            border: none;
            border-bottom: 2px solid #334155;
            padding: 8px;
        }

        /* Scrollbars */
        QScrollBar:vertical {
            background: #0F172A;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #334155;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #38BDF8;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #1E293B;
            color: #94A3B8;
            border-top: 1px solid #334155;
            min-height: 28px;
        }

        QStatusBar::item {
            border: none;
        }

        /* Labels & Stats */
        QLabel.StatValue {
            font-size: 24px;
            font-weight: bold;
            color: #38BDF8;
        }

        QLabel.StatTitle {
            font-size: 12px;
            color: #94A3B8;
            font-weight: 500;
        }
        """

    @staticmethod
    def _ocean_light_qss():
        return """
        QMainWindow, QDialog {
            background-color: #F1F5F9;
            color: #0F172A;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }

        QWidget {
            color: #0F172A;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }

        #SidebarContainer {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
            min-width: 230px;
            max-width: 230px;
        }

        #AppLogoTitle {
            font-size: 18px;
            font-weight: bold;
            color: #0284C7;
            padding: 10px;
        }

        QPushButton.SidebarBtn {
            background-color: transparent;
            color: #64748B;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
        }

        QPushButton.SidebarBtn:hover {
            background-color: #F1F5F9;
            color: #0F172A;
        }

        QPushButton.SidebarBtn:checked, QPushButton.SidebarBtn.active {
            background-color: #0284C7;
            color: #FFFFFF;
            font-weight: bold;
        }

        #HeaderBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            min-height: 55px;
            max-height: 55px;
            padding: 0 15px;
        }

        #HeaderTitle {
            font-size: 18px;
            font-weight: 600;
            color: #0F172A;
        }

        QFrame.CardFrame, QGroupBox {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 15px;
        }

        QGroupBox::title {
            color: #0284C7;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            font-weight: bold;
        }

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }

        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #0284C7;
        }

        QPushButton.PrimaryBtn {
            background-color: #0284C7;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-weight: 600;
        }

        QPushButton.PrimaryBtn:hover {
            background-color: #0369A1;
        }

        QPushButton.SecondaryBtn {
            background-color: #E2E8F0;
            color: #0F172A;
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-weight: 500;
        }

        QPushButton.SecondaryBtn:hover {
            background-color: #CBD5E1;
        }

        QTableWidget, QTableView {
            background-color: #FFFFFF;
            color: #0F172A;
            gridline-color: #E2E8F0;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            selection-background-color: #0284C7;
            selection-color: #FFFFFF;
        }

        QHeaderView::section {
            background-color: #F8FAFC;
            color: #0284C7;
            font-weight: bold;
            border: none;
            border-bottom: 2px solid #E2E8F0;
            padding: 8px;
        }

        QStatusBar {
            background-color: #FFFFFF;
            color: #64748B;
            border-top: 1px solid #E2E8F0;
            min-height: 28px;
        }

        QLabel.StatValue {
            font-size: 24px;
            font-weight: bold;
            color: #0284C7;
        }

        QLabel.StatTitle {
            font-size: 12px;
            color: #64748B;
            font-weight: 500;
        }
        """
