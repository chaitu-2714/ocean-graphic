import os
import chromadb
from chromadb.config import Settings
from config import config

class VectorStoreManager:
    def __init__(self):
        self.chroma_dir = config.get("chroma_dir", "./chroma_db")
        os.makedirs(self.chroma_dir, exist_ok=True)
        self.client = None
        self.paper_collection = None
        self.init_chroma()

    def init_chroma(self):
        try:
            self.client = chromadb.PersistentClient(path=self.chroma_dir)
            self.paper_collection = self.client.get_or_create_collection(
                name="oceanography_papers",
                metadata={"hnsw:space": "cosine"}
            )
            print("ChromaDB initialized successfully.")
        except Exception as e:
            print(f"Error initializing ChromaDB persistent client: {e}")
            self.client = None
            self.paper_collection = None

    def add_paper_chunks(self, paper_id, title, chunks):
        """
        chunks is a list of dicts: [{'section': str, 'content': str}]
        """
        if not self.paper_collection or not chunks:
            return False

        ids = []
        documents = []
        metadatas = []

        for idx, chunk in enumerate(chunks):
            chunk_id = f"paper_{paper_id}_chunk_{idx}"
            ids.append(chunk_id)
            documents.append(chunk.get("content", ""))
            metadatas.append({
                "paper_id": paper_id,
                "title": title,
                "section": chunk.get("section", "Body"),
                "chunk_index": idx
            })

        try:
            self.paper_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"Error adding paper chunks to ChromaDB: {e}")
            return False

    def search_similar_chunks(self, query_text, top_k=5, paper_id=None):
        if not self.paper_collection:
            return []

        try:
            where_clause = None
            if paper_id:
                where_clause = {"paper_id": paper_id}

            results = self.paper_collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where_clause
            )

            matches = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                for doc, meta, cid, dist in zip(docs, metas, ids, distances):
                    matches.append({
                        "id": cid,
                        "content": doc,
                        "paper_id": meta.get("paper_id"),
                        "title": meta.get("title", "Oceanography Research"),
                        "section": meta.get("section", "Body"),
                        "score": round(1.0 - float(dist), 4) if dist is not None else 1.0
                    })

            return matches
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []

vector_store = VectorStoreManager()
