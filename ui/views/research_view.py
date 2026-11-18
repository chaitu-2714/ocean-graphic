import os
import pymupdf as fitz  # PyMuPDF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QLineEdit, QComboBox, QHeaderView,
    QDialog, QTextEdit, QFormLayout, QSplitter, QScrollArea, QSpinBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QColor, QPen

from database import db_manager
from vector_store import vector_store
from utils.pdf_processor import PDFProcessor

class ResearchView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.load_papers()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top Bar
        top_bar = QFrame()
        top_bar.setProperty("class", "CardFrame")
        top_layout = QHBoxLayout(top_bar)

        title = QLabel("Research Paper Digital Library")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        upload_btn = QPushButton("📄 Upload PDF Paper")
        upload_btn.setProperty("class", "PrimaryBtn")
        upload_btn.clicked.connect(self._handle_upload)

        top_layout.addWidget(upload_btn)
        main_layout.addWidget(top_bar)

        # Splitter: Left Table / Right PDF & Summary Workspace
        self.splitter = QSplitter(Qt.Horizontal)

        # Left Paper List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Filters
        filter_card = QFrame()
        filter_card.setProperty("class", "CardFrame")
        filter_layout = QHBoxLayout(filter_card)

        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Search Title / Author / Keyword...")
        self.filter_text.textChanged.connect(self.load_papers)

        filter_layout.addWidget(self.filter_text)
        left_layout.addWidget(filter_card)

        # Papers Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Authors", "Year", "Journal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemClicked.connect(self._on_paper_selected)

        left_layout.addWidget(self.table)
        self.splitter.addWidget(left_widget)

        # Right Detail & PDF Viewer Area
        self.right_widget = QFrame()
        self.right_widget.setProperty("class", "CardFrame")
        self.right_layout = QVBoxLayout(self.right_widget)

        self.empty_lbl = QLabel("Select a research paper from the library to view details, AI summary, and embedded PDF viewer.")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #94A3B8; font-size: 13px;")

        self.right_layout.addWidget(self.empty_lbl)
        self.splitter.addWidget(self.right_widget)

        self.splitter.setSizes([450, 650])
        main_layout.addWidget(self.splitter)

    def load_papers(self):
        search_txt = self.filter_text.text().strip()
        papers = db_manager.get_research_papers(search_text=search_txt)

        self.table.setRowCount(0)
        self.papers_list = papers

        for idx, p in enumerate(papers):
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(p.get("title", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(p.get("authors", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(p.get("publication_year", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(p.get("journal", ""))))

    def _on_paper_selected(self, item):
        row = item.row()
        if row < len(self.papers_list):
            paper = self.papers_list[row]
            self._display_paper_details(paper)

    def _display_paper_details(self, paper):
        # Clear right widget layout
        for i in reversed(range(self.right_layout.count())):
            w = self.right_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        # Paper Title Header
        title_lbl = QLabel(paper.get("title", ""))
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setStyleSheet("color: #38BDF8;")
        title_lbl.setWordWrap(True)

        meta_lbl = QLabel(f"<b>Authors</b>: {paper.get('authors')} | <b>Journal</b>: {paper.get('journal')} ({paper.get('publication_year')})")
        meta_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        self.right_layout.addWidget(title_lbl)
        self.right_layout.addWidget(meta_lbl)

        # AI Summary Box
        summary_card = QFrame()
        summary_card.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px;")
        sum_layout = QVBoxLayout(summary_card)

        sum_title = QLabel("🤖 AI Generated Executive Summary")
        sum_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        sum_title.setStyleSheet("color: #10B981;")

        sum_text = QLabel(
            f"<b>Short Summary</b>: {paper.get('summary_short')}<br><br>"
            f"<b>Key Findings</b>:<br>{paper.get('key_findings')}<br><br>"
            f"<b>Limitations</b>: {paper.get('limitations')}"
        )
        sum_text.setWordWrap(True)
        sum_text.setStyleSheet("font-size: 12px; color: #F8FAFC;")

        sum_layout.addWidget(sum_title)
        sum_layout.addWidget(sum_text)

        self.right_layout.addWidget(summary_card)

        # PDF Viewer Launcher Button & Embedded PDF Canvas
        pdf_path = paper.get("pdf_path", "")
        if pdf_path and os.path.exists(pdf_path):
            pdf_viewer = EmbeddedPDFViewer(pdf_path)
            self.right_layout.addWidget(pdf_viewer)
        else:
            no_pdf = QLabel("PDF file location not found locally.")
            no_pdf.setStyleSheet("color: #E11D48;")
            self.right_layout.addWidget(no_pdf)

    def _handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Research Paper PDF", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            metadata, chunks = PDFProcessor.process_pdf(file_path)

            # Metadata Editor Dialog
            dialog = PaperMetadataEditDialog(metadata, parent=self)
            if dialog.exec() == QDialog.Accepted:
                updated_meta = dialog.get_metadata()
                paper_id = db_manager.insert_research_paper(updated_meta, chunks)
                vector_store.add_paper_chunks(paper_id, updated_meta["title"], chunks)

                QMessageBox.information(self, "Paper Uploaded", "Research paper successfully processed and indexed into ChromaDB!")
                self.load_papers()

        except Exception as e:
            QMessageBox.critical(self, "PDF Processing Error", f"Error processing research paper PDF:\n{str(e)}")

# --- Native PyMuPDF PDF Viewer Widget ---
class EmbeddedPDFViewer(QWidget):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_page = 0
        self.zoom_factor = 1.2
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)

        # Toolbar
        tb = QHBoxLayout()
        prev_btn = QPushButton("◀ Prev")
        prev_btn.clicked.connect(self._prev_page)

        self.page_lbl = QLabel(f"Page 1 of {len(self.doc)}")
        
        next_btn = QPushButton("Next ▶")
        next_btn.clicked.connect(self._next_page)

        zoom_in_btn = QPushButton("🔍 Zoom +")
        zoom_in_btn.clicked.connect(self._zoom_in)

        zoom_out_btn = QPushButton("🔍 Zoom -")
        zoom_out_btn.clicked.connect(self._zoom_out)

        tb.addWidget(prev_btn)
        tb.addWidget(self.page_lbl)
        tb.addWidget(next_btn)
        tb.addStretch()
        tb.addWidget(zoom_in_btn)
        tb.addWidget(zoom_out_btn)

        layout.addLayout(tb)

        # Scroll Area with Page Label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.canvas_label = QLabel()
        self.canvas_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.canvas_label)

        layout.addWidget(self.scroll_area)

        self._render_page()

    def _render_page(self):
        if 0 <= self.current_page < len(self.doc):
            page = self.doc.load_page(self.current_page)
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)

            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)

            self.canvas_label.setPixmap(pixmap)
            self.page_lbl.setText(f"Page {self.current_page + 1} of {len(self.doc)}")

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        if self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self._render_page()

    def _zoom_in(self):
        self.zoom_factor += 0.2
        self._render_page()

    def _zoom_out(self):
        if self.zoom_factor > 0.6:
            self.zoom_factor -= 0.2
            self._render_page()

class PaperMetadataEditDialog(QDialog):
    def __init__(self, metadata, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Research Paper Metadata")
        self.resize(550, 450)
        self.metadata = metadata
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Confirm Extracted Paper Metadata")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #38BDF8;")
        layout.addWidget(title)

        form = QFormLayout()

        self.txt_title = QLineEdit(self.metadata.get("title", ""))
        self.txt_authors = QLineEdit(self.metadata.get("authors", ""))
        self.txt_journal = QLineEdit(self.metadata.get("journal", ""))
        self.txt_year = QLineEdit(str(self.metadata.get("publication_year", 2024)))
        self.txt_doi = QLineEdit(self.metadata.get("doi", ""))
        self.txt_abstract = QTextEdit(self.metadata.get("abstract", ""))

        form.addRow("Title:", self.txt_title)
        form.addRow("Authors:", self.txt_authors)
        form.addRow("Journal:", self.txt_journal)
        form.addRow("Year:", self.txt_year)
        form.addRow("DOI:", self.txt_doi)
        form.addRow("Abstract:", self.txt_abstract)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save & Index Paper")
        save_btn.setProperty("class", "PrimaryBtn")
        save_btn.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)

    def get_metadata(self):
        self.metadata["title"] = self.txt_title.text().strip()
        self.metadata["authors"] = self.txt_authors.text().strip()
        self.metadata["journal"] = self.txt_journal.text().strip()
        try:
            self.metadata["publication_year"] = int(self.txt_year.text().strip())
        except ValueError:
            self.metadata["publication_year"] = 2024
        self.metadata["doi"] = self.txt_doi.text().strip()
        self.metadata["abstract"] = self.txt_abstract.toPlainText().strip()
        return self.metadata
