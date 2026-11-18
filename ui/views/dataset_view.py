import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QLineEdit, QComboBox, QHeaderView,
    QDialog, QTextEdit, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import db_manager
from utils.dataset_processor import DatasetProcessor

class DatasetView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.load_datasets()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top Action Bar
        top_bar = QFrame()
        top_bar.setProperty("class", "CardFrame")
        top_layout = QHBoxLayout(top_bar)

        title = QLabel("Dataset Manager")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        import_btn = QPushButton("📥 Import Dataset (CSV / Excel / NetCDF)")
        import_btn.setProperty("class", "PrimaryBtn")
        import_btn.clicked.connect(self._handle_import)

        sample_btn = QPushButton("✨ Load Sample Argo Dataset")
        sample_btn.setProperty("class", "SecondaryBtn")
        sample_btn.clicked.connect(self._handle_sample_load)

        top_layout.addWidget(import_btn)
        top_layout.addWidget(sample_btn)

        layout.addWidget(top_bar)

        # Filter Bar
        filter_card = QFrame()
        filter_card.setProperty("class", "CardFrame")
        filter_layout = QHBoxLayout(filter_card)

        self.filter_float = QLineEdit()
        self.filter_float.setPlaceholderText("Filter Float ID...")
        self.filter_float.textChanged.connect(self.load_datasets)

        self.filter_region = QComboBox()
        self.filter_region.addItems(["All Regions", "Bay of Bengal", "Arabian Sea", "Equatorial Indian Ocean", "Andaman Sea"])
        self.filter_region.currentTextChanged.connect(self.load_datasets)

        self.filter_min_temp = QLineEdit()
        self.filter_min_temp.setPlaceholderText("Min Temp (°C)")
        self.filter_min_temp.textChanged.connect(self.load_datasets)

        self.filter_max_temp = QLineEdit()
        self.filter_max_temp.setPlaceholderText("Max Temp (°C)")
        self.filter_max_temp.textChanged.connect(self.load_datasets)

        filter_layout.addWidget(QLabel("Float ID:"))
        filter_layout.addWidget(self.filter_float)
        filter_layout.addWidget(QLabel("Region:"))
        filter_layout.addWidget(self.filter_region)
        filter_layout.addWidget(QLabel("Temp Range:"))
        filter_layout.addWidget(self.filter_min_temp)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.filter_max_temp)

        layout.addWidget(filter_card)

        # Datasets Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Float ID", "Region", "Latitude", "Longitude", "Depth (m)",
            "Temp (°C)", "Salinity (PSU)", "Date / Time", "Source File"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

    def load_datasets(self):
        float_id = self.filter_float.text().strip()
        region = self.filter_region.currentText()
        min_temp = self.filter_min_temp.text().strip()
        max_temp = self.filter_max_temp.text().strip()

        records = db_manager.search_datasets(
            float_id=float_id,
            region=region,
            min_temp=min_temp if min_temp else None,
            max_temp=max_temp if max_temp else None
        )

        self.table.setRowCount(0)
        for r in records:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(r.get("float_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(r.get("region", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{r.get('latitude', 0.0):.4f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{r.get('longitude', 0.0):.4f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{r.get('depth', 0.0):.1f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{r.get('temperature', 0.0):.2f}"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"{r.get('salinity', 0.0):.2f}"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(r.get("date_time", ""))))
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(r.get("source_file", ""))))

    def _handle_import(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Oceanographic Dataset", "",
            "Dataset Files (*.csv *.xlsx *.xls *.nc *.netcdf);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;NetCDF Files (*.nc)"
        )

        if not file_path:
            return

        try:
            records, report = DatasetProcessor.load_and_validate(file_path)
            
            # Show Preview & Validation Report Dialog
            dialog = DatasetImportPreviewDialog(records, report, parent=self)
            if dialog.exec() == QDialog.Accepted:
                db_manager.insert_dataset_records(records)
                QMessageBox.information(
                    self, "Import Successful",
                    f"Successfully imported {len(records)} verified oceanographic records into SQLite!"
                )
                self.load_datasets()

        except Exception as e:
            QMessageBox.critical(self, "Import Validation Failed", f"Dataset validation error:\n{str(e)}")

    def _handle_sample_load(self):
        csv_path = DatasetProcessor.create_sample_dataset()
        records, report = DatasetProcessor.load_and_validate(csv_path)
        db_manager.insert_dataset_records(records)
        QMessageBox.information(self, "Sample Dataset Loaded", f"Loaded {len(records)} sample Argo dataset records into database.")
        self.load_datasets()

class DatasetImportPreviewDialog(QDialog):
    def __init__(self, records, report, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dataset Cleaning & Validation Summary")
        self.resize(700, 500)
        self.records = records
        self.report = report
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        lbl = QLabel(f"File Validation Summary for: {self.report['source_file']}")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl.setStyleSheet("color: #38BDF8;")
        layout.addWidget(lbl)

        summary_text = (
            f"• Total Rows Read: {self.report['total_rows_read']}\n"
            f"• Valid Rows Ready for Import: {self.report['valid_rows_imported']}\n"
            f"• Rejected / Cleaned Rows: {self.report['rejected_rows']}\n"
        )
        if self.report['warnings']:
            summary_text += "\nValidation Warnings & Actions:\n"
            for w in self.report['warnings']:
                summary_text += f" - {w}\n"

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(summary_text)
        layout.addWidget(text_edit)

        btn_box = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton(f"Confirm & Import {len(self.records)} Rows")
        confirm_btn.setProperty("class", "PrimaryBtn")
        confirm_btn.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(confirm_btn)

        layout.addLayout(btn_box)
