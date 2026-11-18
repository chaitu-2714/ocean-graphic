import re
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QLineEdit,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QScrollArea,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import db_manager
from vector_store import vector_store
from ollama_client import ollama_client

class SemanticSearchView(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {"id": 1}
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Query Input Header Card
        query_card = QFrame()
        query_card.setProperty("class", "CardFrame")
        query_layout = QVBoxLayout(query_card)

        q_title = QLabel("Natural Language Oceanographic RAG Search")
        q_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        q_title.setStyleSheet("color: #38BDF8;")

        input_box = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Ask a natural language query (e.g., 'Show temperature trend in Bay of Bengal between 2021 and 2024')...")
        self.query_input.setFont(QFont("Segoe UI", 13))
        self.query_input.returnPressed.connect(self._execute_search)

        search_btn = QPushButton("🚀 Run Semantic Search")
        search_btn.setProperty("class", "PrimaryBtn")
        search_btn.clicked.connect(self._execute_search)

        input_box.addWidget(self.query_input)
        input_box.addWidget(search_btn)

        # Quick Examples
        ex_layout = QHBoxLayout()
        ex_lbl = QLabel("Try examples:")
        ex_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        
        ex1 = QPushButton("Bay of Bengal temperature 2021-2024")
        ex1.setStyleSheet("color: #38BDF8; border: none; background: transparent; text-decoration: underline;")
        ex1.clicked.connect(lambda: self._set_query("Show temperature trend in Bay of Bengal between 2021 and 2024"))

        ex2 = QPushButton("Compare Bay of Bengal and Arabian Sea salinity")
        ex2.setStyleSheet("color: #38BDF8; border: none; background: transparent; text-decoration: underline;")
        ex2.clicked.connect(lambda: self._set_query("Compare salinity profiles between Bay of Bengal and Arabian Sea"))

        ex3 = QPushButton("Dissolved oxygen variations in subsurface depths")
        ex3.setStyleSheet("color: #38BDF8; border: none; background: transparent; text-decoration: underline;")
        ex3.clicked.connect(lambda: self._set_query("Explain dissolved oxygen variation in subsurface depth profiles"))

        ex_layout.addWidget(ex_lbl)
        ex_layout.addWidget(ex1)
        ex_layout.addWidget(ex2)
        ex_layout.addWidget(ex3)
        ex_layout.addStretch()

        query_layout.addWidget(q_title)
        query_layout.addLayout(input_box)
        query_layout.addLayout(ex_layout)

        main_layout.addWidget(query_card)

        # Scroll Area for RAG Results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(20)

        # Placeholder Welcome Message
        self.placeholder_lbl = QLabel("Enter a natural language question above to query vector indexed research papers and Argo datasets simultaneously.")
        self.placeholder_lbl.setAlignment(Qt.AlignCenter)
        self.placeholder_lbl.setStyleSheet("color: #94A3B8; font-size: 14px; margin-top: 40px;")
        self.results_layout.addWidget(self.placeholder_lbl)

        self.scroll_area.setWidget(self.results_container)
        main_layout.addWidget(self.scroll_area)

    def _set_query(self, text):
        self.query_input.setText(text)
        self.query_input.setFocus()
        self._execute_search()

    def _execute_search(self):
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a query to search.")
            return

        # 1. Parse Intent & Entities
        intent_info = self._parse_query_intent(query)

        # 2. Retrieve Matched Research Paper Chunks (ChromaDB Vector Store)
        matched_chunks = vector_store.search_similar_chunks(query, top_k=5)

        # 3. Retrieve Matched Argo Datasets (SQLite Relational Search)
        matched_datasets = db_manager.search_datasets(
            region=intent_info.get("region"),
            date_from=intent_info.get("date_from"),
            date_to=intent_info.get("date_to"),
            limit=150
        )

        # 4. Generate RAG Synthesis via Ollama / Fallback Engine
        answer_text, engine_name = ollama_client.generate_rag_synthesis(
            query, matched_datasets, matched_chunks
        )

        # 5. Log Search History
        user_id = self.current_user.get("id", 1) if self.current_user else 1
        db_manager.add_search_history(
            user_id=user_id,
            query=query,
            intent=intent_info.get("intent", "General Query"),
            filters_json=intent_info,
            result_count=len(matched_datasets) + len(matched_chunks)
        )

        # 6. Render Results Layout
        self._render_results(query, intent_info, answer_text, engine_name, matched_datasets, matched_chunks)

    def _parse_query_intent(self, query):
        q_lower = query.lower()
        
        # Region Detection
        region = "All Regions"
        if "bay of bengal" in q_lower or "bengal" in q_lower:
            region = "Bay of Bengal"
        elif "arabian" in q_lower:
            region = "Arabian Sea"
        elif "andaman" in q_lower:
            region = "Andaman Sea"
        elif "equatorial" in q_lower or "indian ocean" in q_lower:
            region = "Equatorial Indian Ocean"

        # Date Range Detection
        year_matches = re.findall(r'\b(20\d\d)\b', query)
        date_from, date_to = None, None
        if len(year_matches) >= 2:
            date_from = f"{year_matches[0]}-01-01"
            date_to = f"{year_matches[1]}-12-31"
        elif len(year_matches) == 1:
            date_from = f"{year_matches[0]}-01-01"
            date_to = f"{year_matches[0]}-12-31"

        intent = "Data Trend Analysis"
        if "paper" in q_lower or "study" in q_lower or "literature" in q_lower:
            intent = "Literature Review"
        elif "compare" in q_lower or "versus" in q_lower or "vs" in q_lower:
            intent = "Regional Comparison"

        return {
            "intent": intent,
            "region": region,
            "date_from": date_from,
            "date_to": date_to
        }

    def _render_results(self, query, intent_info, answer_text, engine_name, datasets, chunks):
        # Clear container
        for i in reversed(range(self.results_layout.count())):
            w = self.results_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        # TOP: AI Synthesis Card
        card_ai = QFrame()
        card_ai.setProperty("class", "CardFrame")
        layout_ai = QVBoxLayout(card_ai)

        ai_header = QHBoxLayout()
        ai_title = QLabel(f"🤖 AI RAG Scientific Synthesis ({engine_name})")
        ai_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ai_title.setStyleSheet("color: #10B981;")

        intent_badge = QLabel(f"Intent: {intent_info['intent']} | Region: {intent_info['region']}")
        intent_badge.setStyleSheet("background-color: #0284C7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")

        ai_header.addWidget(ai_title)
        ai_header.addStretch()
        ai_header.addWidget(intent_badge)

        ai_body = QTextEdit()
        ai_body.setReadOnly(True)
        ai_body.setMarkdown(answer_text)
        ai_body.setMinimumHeight(240)

        layout_ai.addLayout(ai_header)
        layout_ai.addWidget(ai_body)

        self.results_layout.addWidget(card_ai)

        # MIDDLE: Matching Argo Datasets Table
        card_ds = QFrame()
        card_ds.setProperty("class", "CardFrame")
        layout_ds = QVBoxLayout(card_ds)

        ds_title = QLabel(f"📊 Matched Argo Oceanographic Datasets ({len(datasets)} profiles found)")
        ds_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ds_title.setStyleSheet("color: #38BDF8;")
        layout_ds.addWidget(ds_title)

        table_ds = QTableWidget()
        table_ds.setColumnCount(7)
        table_ds.setHorizontalHeaderLabels(["Float ID", "Region", "Lat", "Lon", "Depth (m)", "Temp (°C)", "Salinity (PSU)"])
        table_ds.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for d in datasets[:50]:
            r_idx = table_ds.rowCount()
            table_ds.insertRow(r_idx)
            table_ds.setItem(r_idx, 0, QTableWidgetItem(str(d.get("float_id"))))
            table_ds.setItem(r_idx, 1, QTableWidgetItem(str(d.get("region"))))
            table_ds.setItem(r_idx, 2, QTableWidgetItem(f"{d.get('latitude',0):.2f}"))
            table_ds.setItem(r_idx, 3, QTableWidgetItem(f"{d.get('longitude',0):.2f}"))
            table_ds.setItem(r_idx, 4, QTableWidgetItem(f"{d.get('depth',0):.1f}"))
            table_ds.setItem(r_idx, 5, QTableWidgetItem(f"{d.get('temperature',0):.2f}"))
            table_ds.setItem(r_idx, 6, QTableWidgetItem(f"{d.get('salinity',0):.2f}"))

        table_ds.setMaximumHeight(200)
        layout_ds.addWidget(table_ds)
        self.results_layout.addWidget(card_ds)

        # BELOW: Matched Research Papers (ChromaDB Vector Results)
        card_papers = QFrame()
        card_papers.setProperty("class", "CardFrame")
        layout_p = QVBoxLayout(card_papers)

        p_title = QLabel(f"📚 Semantic Vector Matched Literature Excerpts ({len(chunks)} chunks)")
        p_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        p_title.setStyleSheet("color: #38BDF8;")
        layout_p.addWidget(p_title)

        if chunks:
            for c in chunks:
                chunk_box = QFrame()
                chunk_box.setStyleSheet("background-color: #0F172A; border-radius: 6px; padding: 10px;")
                cb_layout = QVBoxLayout(chunk_box)

                c_header = QLabel(f"<b>{c.get('title')}</b> — Section: <i>{c.get('section')}</i> (Score: {c.get('score', 1.0)})")
                c_header.setStyleSheet("color: #38BDF8; font-size: 12px;")

                c_text = QLabel(c.get("content", "")[:350] + "...")
                c_text.setWordWrap(True)
                c_text.setStyleSheet("color: #CBD5E1; font-size: 12px;")

                cb_layout.addWidget(c_header)
                cb_layout.addWidget(c_text)
                layout_p.addWidget(chunk_box)
        else:
            no_c = QLabel("No direct research paper excerpts matched the query embedding threshold.")
            no_c.setStyleSheet("color: #94A3B8;")
            layout_p.addWidget(no_c)

        self.results_layout.addWidget(card_papers)

        # BOTTOM: Embedded Matplotlib Visual Trend Chart
        chart_card = QFrame()
        chart_card.setProperty("class", "CardFrame")
        chart_layout = QVBoxLayout(chart_card)

        chart_title = QLabel("📈 Interactive Oceanographic Parameter Chart")
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        chart_title.setStyleSheet("color: #38BDF8;")
        chart_layout.addWidget(chart_title)

        canvas = MatplotlibCanvas(datasets)
        chart_layout.addWidget(canvas)

        self.results_layout.addWidget(chart_card)

# --- Embedded Matplotlib Canvas Widget ---
class MatplotlibCanvas(FigureCanvas):
    def __init__(self, datasets, parent=None):
        fig = Figure(figsize=(8, 3.5), facecolor='#1E293B')
        super().__init__(fig)
        self.setParent(parent)
        self._plot(datasets)

    def _plot(self, datasets):
        self.figure.clear()

        # Dark theme styling for Matplotlib
        ax1 = self.figure.add_subplot(121, facecolor='#0F172A')
        ax2 = self.figure.add_subplot(122, facecolor='#0F172A')

        if datasets:
            depths = [d['depth'] for d in datasets]
            temps = [d['temperature'] for d in datasets]
            salinities = [d['salinity'] for d in datasets]

            # Temp vs Depth Profile
            ax1.scatter(temps, depths, color='#38BDF8', alpha=0.7, s=20)
            ax1.invert_yaxis()
            ax1.set_title('Temperature vs Depth Profile', color='#F8FAFC', fontsize=11, fontweight='bold')
            ax1.set_xlabel('Temperature (°C)', color='#94A3B8')
            ax1.set_ylabel('Depth (m)', color='#94A3B8')
            ax1.tick_params(colors='#94A3B8')

            # Salinity vs Depth Profile
            ax2.scatter(salinities, depths, color='#10B981', alpha=0.7, s=20)
            ax2.invert_yaxis()
            ax2.set_title('Salinity vs Depth Profile', color='#F8FAFC', fontsize=11, fontweight='bold')
            ax2.set_xlabel('Salinity (PSU)', color='#94A3B8')
            ax2.set_ylabel('Depth (m)', color='#94A3B8')
            ax2.tick_params(colors='#94A3B8')

        else:
            ax1.text(0.5, 0.5, 'No profile data to plot', color='#94A3B8', ha='center', va='center')
            ax2.text(0.5, 0.5, 'No profile data to plot', color='#94A3B8', ha='center', va='center')

        self.figure.tight_layout()
        self.draw()
