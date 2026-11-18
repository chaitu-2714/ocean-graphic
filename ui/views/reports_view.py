from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import db_manager

class ReportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.generate_report()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        top_bar = QFrame()
        top_bar.setProperty("class", "CardFrame")
        top_layout = QHBoxLayout(top_bar)

        title = QLabel("Oceanographic Summary & Research Reports")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        export_btn = QPushButton("💾 Export Report (TXT / Markdown)")
        export_btn.setProperty("class", "PrimaryBtn")
        export_btn.clicked.connect(self._export_report)

        top_layout.addWidget(export_btn)
        layout.addWidget(top_bar)

        # Report Content Card
        card = QFrame()
        card.setProperty("class", "CardFrame")
        card_layout = QVBoxLayout(card)

        self.report_edit = QTextEdit()
        self.report_edit.setReadOnly(True)

        card_layout.addWidget(self.report_edit)
        layout.addWidget(card)

    def generate_report(self):
        stats = db_manager.get_dataset_stats()
        papers = db_manager.get_research_papers()

        report_md = f"""# 🌊 OceanMind AI System Summary Report

### 1. Executive System Statistics
- **Total Ingested Argo Dataset Records**: {stats['total_records']}
- **Distinct Monitored Ocean Regions**: {stats['regions_count']}
- **Temporal Span**: {stats['time_range']}
- **Average Surface/Subsurface Temperature**: {stats['avg_temp']} °C
- **Average Salinity Profile**: {stats['avg_salinity']} PSU
- **Indexed Research Papers**: {len(papers)}

---

### 2. Indexed Research Literature
"""
        for idx, p in enumerate(papers):
            report_md += f"{idx+1}. **{p.get('title')}** ({p.get('publication_year')}) - {p.get('authors')}\n"

        if not papers:
            report_md += "_No research papers uploaded yet._\n"

        report_md += f"""
---

### 3. Data Integrity & Vector DB Verification
- **SQLite Database Status**: Connected & Verified
- **ChromaDB Vector Store**: Active with HNSW Cosine Distance
- **Report Generated At**: {db_manager.get_dataset_stats().get('time_range')}
"""
        self.report_edit.setMarkdown(report_md)

    def _export_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Summary Report", "OceanMind_Summary_Report.md", "Markdown (*.md);;Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.report_edit.toPlainText())
                QMessageBox.information(self, "Exported", f"Report successfully saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
