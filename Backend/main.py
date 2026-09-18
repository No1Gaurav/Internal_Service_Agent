'''from config import KNOWLEDGE_BASE_DIR, create_directories
from classifier import RequestClassifier
from knowledge_base import KnowledgeBase


def main():

    create_directories()

    classifier = RequestClassifier()
    kb = KnowledgeBase(KNOWLEDGE_BASE_DIR)

    request = input("Enter employee request: ")

    category = classifier.classify(request)

    print("\nCategory:", category)

    results = kb.search(request)

    print("\nKnowledge Base Results:")

    for result in results[:3]:
        print(
            f"- {result['document']} "
            f"(score={result['score']})"
        )


if __name__ == "__main__":
    main()'''

from config import KNOWLEDGE_BASE_DIR, VECTOR_STORE_DIR
from rag import RAGSystem
from llm import generate_response


def main():

    print("Initializing RAG system...")

    rag = RAGSystem(
        KNOWLEDGE_BASE_DIR,
        VECTOR_STORE_DIR
    )

    rag.initialize()

    print("\nRAG system ready.")

    while True:

        query = input(
            "\nEmployee request "
            "(type 'exit' to quit): "
        )

        if query.lower() == "exit":
            break

        results = rag.search(
            query,
            top_k=3
        )

        print("\nRetrieved policies:")

        for result in results:
            print(
                f"- {result['source']} "
                f"({result['score']:.3f})"
            )

        print("\nGenerating response...")
        print(results)

        answer = generate_response(
            query,
            results
        )

        print("\n" + "=" * 70)
        print("AI SUPPORT RESPONSE")
        print("=" * 70)

        print(answer)

        print("=" * 70)


if __name__ == "__main__":
    main()