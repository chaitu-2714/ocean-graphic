import sqlite3
import bcrypt
import json
import os
from datetime import datetime
from config import config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.get("db_path", "oceanmind.db")
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    institution TEXT DEFAULT '',
                    photo_path TEXT DEFAULT '',
                    recovery_question TEXT DEFAULT 'What is your favorite ocean?',
                    recovery_answer TEXT DEFAULT 'Pacific',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Session table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            # Search history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    intent TEXT DEFAULT '',
                    filters_json TEXT DEFAULT '{}',
                    result_count INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            # System logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)

            # Datasets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    float_id TEXT DEFAULT 'N/A',
                    region TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    depth REAL NOT NULL,
                    temperature REAL NOT NULL,
                    salinity REAL NOT NULL,
                    dissolved_oxygen REAL DEFAULT 0.0,
                    date_time TEXT NOT NULL,
                    source_file TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Research papers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    authors TEXT DEFAULT '',
                    journal TEXT DEFAULT '',
                    publication_year INTEGER DEFAULT 2024,
                    doi TEXT DEFAULT '',
                    abstract TEXT DEFAULT '',
                    keywords TEXT DEFAULT '',
                    pdf_path TEXT NOT NULL,
                    summary_short TEXT DEFAULT '',
                    key_findings TEXT DEFAULT '',
                    limitations TEXT DEFAULT '',
                    future_work TEXT DEFAULT '',
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Paper text chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paper_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id INTEGER NOT NULL,
                    section TEXT DEFAULT 'Main Body',
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(paper_id) REFERENCES research_papers(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

            # Set default theme in settings if not present
            cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO settings (key, value) VALUES ('theme', 'Ocean Dark')")
                conn.commit()
            
            # Ensure default demo user exists if table empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                demo_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, institution, recovery_question, recovery_answer)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("Dr. Oceanographer", "admin@oceanmind.ai", demo_pw, "National Institute of Oceanography", "What is your favorite ocean?", "Indian Ocean"))
                conn.commit()

    def log(self, level, component, message):
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(
                    "INSERT INTO logs (level, component, message) VALUES (?, ?, ?)",
                    (level, component, message)
                )
                conn.commit()
        except Exception:
            pass

    # --- User Authentication ---
    def register_user(self, name, email, password, institution="", recovery_question="", recovery_answer=""):
        email = email.strip().lower()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "An account with this email already exists."

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, institution, recovery_question, recovery_answer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, hashed_pw, institution, recovery_question, recovery_answer))
            conn.commit()
            self.log("INFO", "Auth", f"New user registered: {email}")
            return True, "Registration successful."

    def authenticate_user(self, email, password):
        email = email.strip().lower()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "Invalid email or password.", None

            stored_hash = user["password_hash"].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                user_dict = dict(user)
                # Create session record
                token = os.urandom(16).hex()
                cursor.execute("INSERT INTO session (user_id, token) VALUES (?, ?)", (user["id"], token))
                conn.commit()
                self.log("INFO", "Auth", f"User logged in: {email}")
                return True, "Login successful.", user_dict
            else:
                return False, "Invalid email or password.", None

    def reset_password(self, email, recovery_answer, new_password):
        email = email.strip().lower()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found."
            
            if user["recovery_answer"].strip().lower() != recovery_answer.strip().lower():
                return False, "Incorrect recovery answer."

            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))
            conn.commit()
            self.log("INFO", "Auth", f"Password reset for: {email}")
            return True, "Password updated successfully."

    def update_user_profile(self, user_id, name, institution, photo_path=""):
        with self.get_connection() as conn:
            conn.cursor().execute("""
                UPDATE users SET name = ?, institution = ?, photo_path = ? WHERE id = ?
            """, (name, institution, photo_path, user_id))
            conn.commit()
            return True

    def get_theme(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
            row = cursor.fetchone()
            return row["value"] if row else "Ocean Dark"

    def set_theme(self, theme_name):
        with self.get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO settings (key, value) VALUES ('theme', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (theme_name,))
            conn.commit()
            config.set("theme", theme_name)

    # --- Dataset Methods ---
    def insert_dataset_records(self, records):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO datasets (float_id, region, latitude, longitude, depth, temperature, salinity, dissolved_oxygen, date_time, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(
                r.get("float_id", "N/A"),
                r.get("region", "Bay of Bengal"),
                float(r.get("latitude", 0.0)),
                float(r.get("longitude", 0.0)),
                float(r.get("depth", 0.0)),
                float(r.get("temperature", 0.0)),
                float(r.get("salinity", 0.0)),
                float(r.get("dissolved_oxygen", 0.0)),
                str(r.get("date_time", "2024-01-01")),
                r.get("source_file", "")
            ) for r in records])
            conn.commit()

    def get_dataset_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM datasets")
            total_records = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT region) FROM datasets")
            unique_regions = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(date_time), MAX(date_time) FROM datasets")
            min_date, max_date = cursor.fetchone()

            cursor.execute("SELECT AVG(temperature), AVG(salinity) FROM datasets")
            avg_temp, avg_sal = cursor.fetchone()

            cursor.execute("SELECT source_file FROM datasets ORDER BY id DESC LIMIT 1")
            last_import = cursor.fetchone()

            return {
                "total_records": total_records or 0,
                "regions_count": unique_regions or 0,
                "time_range": f"{min_date or 'N/A'} to {max_date or 'N/A'}",
                "avg_temp": round(avg_temp, 2) if avg_temp else 0.0,
                "avg_salinity": round(avg_sal, 2) if avg_sal else 0.0,
                "last_imported": last_import[0] if last_import else "None"
            }

    def search_datasets(self, float_id=None, region=None, date_from=None, date_to=None, min_depth=None, max_depth=None, min_temp=None, max_temp=None, limit=500):
        query = "SELECT * FROM datasets WHERE 1=1"
        params = []

        if float_id:
            query += " AND float_id LIKE ?"
            params.append(f"%{float_id}%")
        if region and region != "All Regions":
            query += " AND region LIKE ?"
            params.append(f"%{region}%")
        if date_from:
            query += " AND date_time >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date_time <= ?"
            params.append(date_to)
        if min_depth is not None and str(min_depth).strip():
            query += " AND depth >= ?"
            params.append(float(min_depth))
        if max_depth is not None and str(max_depth).strip():
            query += " AND depth <= ?"
            params.append(float(max_depth))
        if min_temp is not None and str(min_temp).strip():
            query += " AND temperature >= ?"
            params.append(float(min_temp))
        if max_temp is not None and str(max_temp).strip():
            query += " AND temperature <= ?"
            params.append(float(max_temp))

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # --- Research Paper Methods ---
    def insert_research_paper(self, paper_data, chunks):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO research_papers (title, authors, journal, publication_year, doi, abstract, keywords, pdf_path, summary_short, key_findings, limitations, future_work)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_data.get("title", "Untitled Paper"),
                paper_data.get("authors", "Unknown Author"),
                paper_data.get("journal", "Oceanography Journal"),
                int(paper_data.get("publication_year", 2024)),
                paper_data.get("doi", ""),
                paper_data.get("abstract", ""),
                paper_data.get("keywords", ""),
                paper_data.get("pdf_path", ""),
                paper_data.get("summary_short", ""),
                paper_data.get("key_findings", ""),
                paper_data.get("limitations", ""),
                paper_data.get("future_work", "")
            ))
            paper_id = cursor.lastrowid

            cursor.executemany("""
                INSERT INTO paper_chunks (paper_id, section, chunk_index, content)
                VALUES (?, ?, ?, ?)
            """, [(paper_id, c.get("section", "Body"), idx, c.get("content", "")) for idx, c in enumerate(chunks)])

            conn.commit()
            return paper_id

    def get_research_papers(self, search_text="", year=None, journal=None):
        query = "SELECT * FROM research_papers WHERE 1=1"
        params = []
        if search_text:
            query += " AND (title LIKE ? OR authors LIKE ? OR keywords LIKE ? OR abstract LIKE ?)"
            term = f"%{search_text}%"
            params.extend([term, term, term, term])
        if year and year != "All Years":
            query += " AND publication_year = ?"
            params.append(int(year))
        if journal and journal != "All Journals":
            query += " AND journal LIKE ?"
            params.append(f"%{journal}%")

        query += " ORDER BY id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_paper_by_id(self, paper_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM research_papers WHERE id = ?", (paper_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- Search History ---
    def add_search_history(self, user_id, query, intent, filters_json, result_count):
        with self.get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO search_history (user_id, query, intent, filters_json, result_count)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, query, intent, json.dumps(filters_json), result_count))
            conn.commit()

    def get_search_history(self, user_id, limit=20):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM search_history WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

db_manager = DatabaseManager()
