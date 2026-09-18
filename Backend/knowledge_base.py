from pathlib import Path


class KnowledgeBase:
    def __init__(self, kb_directory: Path):
        self.kb_directory = kb_directory

    def load_documents(self) -> dict[str, str]:
        """Load all knowledge-base text/markdown files."""

        documents = {}

        for file_path in self.kb_directory.iterdir():

            if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md"}:
                documents[file_path.name] = file_path.read_text(
                    encoding="utf-8"
                )

        return documents

    def search(self, query: str) -> list[dict]:
        """
        Simple keyword-based search.

        This is intentionally basic for the first version.
        Later we can replace it with semantic/vector retrieval.
        """

        documents = self.load_documents()

        query_words = set(query.lower().split())

        results = []

        for filename, content in documents.items():

            content_lower = content.lower()

            score = sum(
                1
                for word in query_words
                if word in content_lower
            )

            if score > 0:
                results.append({
                    "document": filename,
                    "score": score,
                    "content": content
                })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results