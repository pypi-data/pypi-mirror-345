import os
import pickle
from langchain.schema import Document
from langchain.retrievers import BM25Retriever
class PersistentBM25Retriever(BM25Retriever):
    def persist(self, save_dir: str):
        """Save the retriever to a directory."""
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "bm25.pkl")

        with open(save_path, "wb") as f:
            pickle.dump(self, f)
        print(f"BM25Retriever saved to {save_path}")

    @classmethod
    def from_persist_dir(cls, save_dir: str):
        """Load the retriever from a directory."""
        save_path = os.path.join(save_dir, "bm25.pkl")

        if not os.path.exists(save_path):
            raise FileNotFoundError(f"No BM25Retriever found at {save_path}")

        with open(save_path, "rb") as f:
            retriever = pickle.load(f)

        print(f"BM25Retriever loaded from {save_path}")
        return retriever    