# persistent_bm25

persistent_bm25 is a Python package that provides a persistent implementation of BM25 retrieval.

## Installation

You can install it via pip:

```bash
pip install persistent_bm25
```


## Usage

```python
from persistent_bm25 import PersistentBM25Retriever
from langchain_core.documents import Document
docs = [
    Document(page_content="LangChain makes AI powerful"),
    Document(page_content="BM25 is a ranking function for search"),
]

# Create retriever
bm25_retriever = PersistentBM25Retriever.from_documents(docs)
bm25_retriever.persist("./bm25_retriever")

loaded_bm25_retriever = PersistentBM25Retriever.from_persist_dir("./bm25_retriever")

results = loaded_bm25_retriever.get_relevant_documents("AI search")
print(results)
```
