"""
=============================================================
PIPELINE INDEXING — RAG UTS Data Engineering
=============================================================

Pipeline ini dijalankan SEKALI untuk:
1. Memuat dokumen dari folder data/
2. Memecah dokumen menjadi chunk-chunk kecil
3. Mengubah setiap chunk menjadi vektor (embedding)
4. Menyimpan vektor ke dalam vector database

Jalankan dengan: python src/indexing.py
=============================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from utils import read_pdf, read_csv, chunk_text
from embeddings import get_embedding_function

# ─── LANGKAH 0: Load konfigurasi dari .env ───────────────────────────────────
load_dotenv()

# Konfigurasi — bisa diubah sesuai kebutuhan
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
DATA_DIR      = Path(os.getenv("DATA_DIR", "./data"))
VS_DIR        = Path(os.getenv("VECTORSTORE_DIR", "./vectorstore"))


def build_index_scratch():
    """Implementasi RAG dari scratch menggunakan ChromaDB + sentence-transformers."""
    import chromadb
    from chromadb.utils import embedding_functions

    print("🚀 Memulai Pipeline Indexing (From Scratch - Chroma DB)")
    chunks_keseluruhan = []
    metadatas = []
    ids = []
    
    # 1. Load Dokumen
    for file_path in DATA_DIR.glob("**/*"):
        teks_dokumen = ""
        
        # Cek ekstensi file dan gunakan fungsi utils yang sesuai
        if file_path.suffix.lower() == '.pdf':
            teks_dokumen = read_pdf(file_path)
        elif file_path.suffix.lower() == '.csv':
            teks_dokumen = read_csv(file_path)
        else:
            continue
            
        if not teks_dokumen.strip():
            continue
            
        # 2. Chunking teks menggunakan fungsi dari utils.py
        potongan_teks = chunk_text(teks_dokumen, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        
        # 3. Siapkan metadata dan id untuk ChromaDB
        for chunk in potongan_teks:
            chunks_keseluruhan.append(chunk)
            metadatas.append({"source": str(file_path.name)})
            ids.append(f"chunk_{len(chunks_keseluruhan)}")
                
    print(f"✂️ {len(chunks_keseluruhan)} chunk dibuat dari {DATA_DIR}")

    # 3. Setup Embedding & Simpan ke ChromaDB lokal
    print("💾 Menyimpan ke Chroma DB...")
    VS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 4. Memanggil fungsi embedding_fuction dari embeddings.py
    ef = get_embedding_function()

    client = chromadb.PersistentClient(path=str(VS_DIR))
    
    # 5. Hapus koleksi lama jika ada
    try:
        client.delete_collection(name="rag_collection")
    except Exception:
        pass
        
    # 6. Buat koleksi baru yang terhubung dengan model embedding
    collection = client.create_collection(name="rag_collection", embedding_function=ef)

    # 7. Masukkan data dengan sistem BATCHING
    MAX_BATCH_SIZE = 5000 
    
    print(f"⏳ Memasukkan total {len(chunks_keseluruhan)} chunk ke ChromaDB...")
    
    for i in range(0, len(chunks_keseluruhan), MAX_BATCH_SIZE):
        batch_docs = chunks_keseluruhan[i : i + MAX_BATCH_SIZE]
        batch_metas = metadatas[i : i + MAX_BATCH_SIZE]
        batch_ids = ids[i : i + MAX_BATCH_SIZE]
        
        # Masukkan per batch
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"  -> Berhasil menyimpan batch: {i + 1} sampai {i + len(batch_docs)}")

    print(f"✅ Index Chroma DB tersimpan di {VS_DIR}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_index_scratch()
