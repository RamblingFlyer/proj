import json
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

DATA_FILE = "data/openmp_prs.json"
OUTPUT_FILE = "models/embeddings.pkl"

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"[ERROR] Could not find {DATA_FILE}. Run download_data.py first.")

# Load pre-trained embedding model
print("[INFO] Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load PR metadata
with open(DATA_FILE, "r") as f:
    prs = json.load(f)

texts = [f"{pr['title']} {pr['body']}" for pr in prs]

# Encode PRs
print(f"[INFO] Generating embeddings for {len(texts)} PRs...")
embeddings = model.encode(texts, show_progress_bar=True)

# Create models/ directory if it doesn’t exist
os.makedirs("models", exist_ok=True)

# Save as a dictionary: {"prs": [...], "embeddings": [...]}
with open(OUTPUT_FILE, "wb") as f:
    pickle.dump({"prs": prs, "embeddings": embeddings}, f)

print(f"[INFO] ✅ Embeddings saved to {OUTPUT_FILE}")
