import os
from chromadb.utils import embedding_functions

def get_embedding_function():
    """
    Menginisialisasi dan mengembalikan fungsi embedding bawaan Chroma.
    """
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    """ganti variabel device dengan nilai cpu bila tidak menggunakan cuda dan jika menggunakan cuda 
    maka install pytorch dengan pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126"""
    device = "cuda" 

    print(f"🧠 Memuat model embedding: {model_name} (Device: {device})...")
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=device
    )
    
    return ef