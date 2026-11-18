# 🌊 OceanMind AI - Oceanographic Intelligence Platform

**OceanMind AI** is a professional desktop application for oceanographic data analysis, semantic search, Argo float profile exploration, and literature synthesis powered by PySide6, SQLite, ChromaDB, and LLM integrations (Google Gemini & Ollama).

---

## 🚀 Features

- **Interactive Oceanographic Dashboard**: Real-time overview of ocean observation metrics, active regions, and ingested data.
- **Argo Dataset Processing**: Ingest and validate oceanographic data from CSV, Excel, or NetCDF formats.
- **Ocean Coordinates & Coverage Map**: Geographic visualization of observation coordinates and sampling locations.
- **Oceanographic Analytics & Profiling**: Deep-dive charts into temperature, salinity, depth profiles, and spatial distributions using Matplotlib.
- **Semantic Literature Search & RAG**: Vector-indexed research paper search using ChromaDB and AI-assisted synthesis with Gemini or local Ollama models.
- **Automated Summary Reporting**: Generate and export comprehensive scientific summary reports in Markdown and TXT formats.
- **Secure Authentication**: Built-in user management with hashed passwords and session management.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/chaitu-2714/ocean-graphic.git
cd ocean-graphic
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys / settings:
```bash
cp .env.example .env
```
Key configuration parameters:
- `LLM_PROVIDER`: `gemini` or `ollama`
- `GEMINI_API_KEY`: Your Google Gemini API Key (if using Gemini)
- `OLLAMA_URL`: URL of your local Ollama server (e.g., `http://localhost:11434`)
- `DB_PATH`: SQLite database file path (defaults to `oceanmind.db`)
- `CHROMA_DIR`: ChromaDB persistent directory (defaults to `chroma_db`)

---

## 🖥️ Running the Application

Launch the desktop UI with:
```bash
python main.py
```

### Default Login Credentials
- **Email:** `admin@oceanmind.ai`
- **Password:** `admin123`

*(You can also create a new account via the Register tab on the login screen).*

---

## 📁 Project Structure

```
├── chroma_db/                  # ChromaDB vector store directory (auto-generated)
├── ui/                         # PySide6 desktop GUI modules
│   ├── views/                  # UI view panels (Dashboard, Analytics, Maps, Research, etc.)
│   ├── login_window.py         # Authentication dialog
│   ├── main_window.py          # Main application window & navigation
│   └── splash_screen.py        # Animated startup splash screen
├── utils/                      # Helper processors (PDF parser, Dataset validator)
├── config.py                   # Configuration loader
├── database.py                 # SQLite database models & query manager
├── main.py                     # Application entry point
├── ollama_client.py            # Ollama & LLM client wrapper
├── sample_argo_bay_of_bengal.csv # Sample dataset for testing
├── theme_manager.py            # Dark/Ocean UI theme manager
├── vector_store.py             # ChromaDB vector indexing manager
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 📄 License
MIT License.
