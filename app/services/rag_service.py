from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pypdf import PdfReader
import os

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

documents = []

#  Smart chunking function
def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks


#  Load TEXT file
if os.path.exists("knowledge/data.txt"):
    with open("knowledge/data.txt", "r", encoding="utf-8") as f:
        text = f.read()
        chunks = chunk_text(text)
        documents.extend(chunks)
        print(f" Loaded {len(chunks)} chunks from data.txt")


#  Load PDF (SAFE)
pdf_path = "knowledge/sample.pdf"

if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
    print(f" Loading PDF: {pdf_path}")
    reader = PdfReader(pdf_path)

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            chunks = chunk_text(text)
            documents.extend(chunks)
            print(f" Page {page_num+1}: {len(chunks)} chunks added")
        else:
            print(f" Page {page_num+1}: No text found")
else:
    print(" No valid PDF found, skipping...")


#  Safety check
if not documents:
    raise ValueError(" No documents found in knowledge folder")

print(f"Total documents loaded: {len(documents)}")


# Normalize embeddings (IMPORTANT)
doc_embeddings = model.encode(documents, normalize_embeddings=True)

# Create FAISS index
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)   # cosine similarity
index.add(np.array(doc_embeddings))


def retrieve_context(query, top_k=3):
    query_vec = model.encode([query], normalize_embeddings=True)
    distances, indices = index.search(np.array(query_vec), top_k)

    results = [documents[i] for i in indices[0]]
    return " ".join(results)