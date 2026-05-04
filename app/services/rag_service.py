from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load data
with open("knowledge/data.txt", "r", encoding="utf-8") as f:
    documents = f.readlines()

# Convert to embeddings
doc_embeddings = model.encode(documents)

# Create FAISS index
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))


def retrieve_context(query, top_k=2):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)

    results = [documents[i] for i in indices[0]]
    return " ".join(results)