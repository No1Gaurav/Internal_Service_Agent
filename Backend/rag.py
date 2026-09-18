from pathlib import Path
import pickle

import faiss
from sentence_transformers import SentenceTransformer


class RAGSystem:

    def __init__(self, knowledge_base_dir: Path, vector_store_dir: Path):

        self.knowledge_base_dir = knowledge_base_dir
        self.vector_store_dir = vector_store_dir

        self.index_path = vector_store_dir / "faiss.index"
        self.chunks_path = vector_store_dir / "chunks.pkl"

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.index = None
        self.chunks = []

    def load_documents(self):

        documents = []

        for file_path in self.knowledge_base_dir.iterdir():

            if (
                file_path.is_file()
                and file_path.suffix.lower() in {".md", ".txt"}
            ):

                content = file_path.read_text(
                    encoding="utf-8"
                )

                documents.append(
                    {
                        "source": file_path.name,
                        "content": content
                    }
                )

        return documents

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        overlap: int = 100
    ):

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk = " ".join(
                words[start:end]
            )

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def build_index(self):

        print("Building vector index...")

        documents = self.load_documents()

        self.chunks = []

        for document in documents:

            chunks = self.chunk_text(
                document["content"]
            )

            for chunk in chunks:

                self.chunks.append(
                    {
                        "source": document["source"],
                        "text": chunk
                    }
                )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        self.vector_store_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(self.index_path)
        )

        with open(
            self.chunks_path,
            "wb"
        ) as f:

            pickle.dump(
                self.chunks,
                f
            )

        print(
            f"Indexed {len(self.chunks)} chunks "
            f"from {len(documents)} documents."
        )

        print("Vector index saved.")

    def load_index(self):

        print("Loading saved vector index...")

        self.index = faiss.read_index(
            str(self.index_path)
        )

        with open(
            self.chunks_path,
            "rb"
        ) as f:

            self.chunks = pickle.load(f)

        print(
            f"Loaded {len(self.chunks)} chunks "
            f"from saved index."
        )

    def initialize(self):

        if (
            self.index_path.exists()
            and self.chunks_path.exists()
        ):

            self.load_index()

        else:

            self.build_index()

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            result = self.chunks[index].copy()

            result["score"] = float(score)

            results.append(result)

        return results