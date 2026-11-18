import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "app_name": "OceanMind AI",
    "version": "1.0.0",
    "theme": "Ocean Dark",
    "db_path": str(BASE_DIR / "oceanmind.db"),
    "chroma_dir": str(BASE_DIR / "chroma_db"),
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3",
    "embedding_model": "all-MiniLM-L6-v2"
}

class Config:
    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    self.data.update(file_data)
            except Exception as e:
                print(f"Error loading config.json: {e}")
        
        # Override with env if present
        if os.getenv("OLLAMA_URL"):
            self.data["ollama_url"] = os.getenv("OLLAMA_URL")
        if os.getenv("DB_PATH"):
            self.data["db_path"] = str(BASE_DIR / os.getenv("DB_PATH"))
        if os.getenv("CHROMA_DIR"):
            self.data["chroma_dir"] = str(BASE_DIR / os.getenv("CHROMA_DIR"))

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

config = Config()
