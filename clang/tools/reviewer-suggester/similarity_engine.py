import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

EMBEDDINGS_FILE = "models/embeddings.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_similar_prs(pr_title, pr_body, top_k=5):
    if not os.path.exists(EMBEDDINGS_FILE):
        raise FileNotFoundError(f"Embeddings file '{EMBEDDINGS_FILE}' not found.")
    
    if os.path.getsize(EMBEDDINGS_FILE) == 0:
        raise ValueError(f"Embeddings file '{EMBEDDINGS_FILE}' is empty. Please regenerate the embeddings.")

    with open(EMBEDDINGS_FILE, "rb") as f:
        try:
            data = pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            raise ValueError(f"Embeddings file '{EMBEDDINGS_FILE}' is corrupted. Please regenerate the embeddings.")
    
    historical_prs = data["prs"]
    historical_embeddings = data["embeddings"]

    query_text = pr_title + " " + pr_body
    query_embedding = model.encode([query_text])
    
    similarities = cosine_similarity(query_embedding, historical_embeddings)[0]
    ranked_indices = similarities.argsort()[::-1][:top_k]
    
    similar_prs = [historical_prs[i] for i in ranked_indices]
    return similar_prs
