import os
import pickle
from typing import Optional
from langchain.retrievers import BM25Retriever
from rank_bm25 import BM25Okapi

class PersistentBM25Retriever(BM25Retriever):
    save_dir: Optional[str] = None

    def __init__(self, **kwargs):
        # Pop the 'persist' parameter from kwargs, defaulting to False
        persist = kwargs.pop("persist", False)
        
        # Map 'documents' to 'docs' for compatibility with BM25Retriever
        if "documents" in kwargs:
            kwargs["docs"] = kwargs.pop("documents")
        
        # Initialize the parent class with the remaining kwargs
        super().__init__(**kwargs)
        
        # If persist is True, ensure save_dir is provided and call persist()
        if persist:
            if not self.save_dir:
                raise ValueError("save_dir must be provided when persist=True")
            self.persist()

    def persist(self):
        """Save the retriever to the specified directory."""
        if not self.save_dir:
            raise ValueError("Save directory not specified.")
        
        os.makedirs(self.save_dir, exist_ok=True)
        save_path = os.path.join(self.save_dir, "bm25.pkl")
        with open(save_path, "wb") as f:
            pickle.dump(self, f)
        print(f"BM25Retriever saved to {save_path}")

    @classmethod
    def from_persist_dir(cls, save_dir: str, k: int = 5):
        """Load the retriever from a directory and set k."""
        save_path = os.path.join(save_dir, "bm25.pkl")
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"No BM25Retriever found at {save_path}")
        
        with open(save_path, "rb") as f:
            retriever = pickle.load(f)
        
        # Rebuild the vectorizer after loading
        retriever.vectorizer = BM25Okapi([doc.page_content for doc in retriever.docs])
        
        retriever.k = k
        retriever.save_dir = save_dir
        return retriever