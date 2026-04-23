import csv
from pypdf import PdfReader

def read_pdf(file_path):
    """Membaca file PDF dan mengembalikan teks utuh."""
    teks = ""
    try:
        reader = PdfReader(file_path)
        for halaman in reader.pages:
            extracted_text = halaman.extract_text()
            if extracted_text:
                teks += extracted_text + "\n"
    except Exception as e:
        print(f"Gagal membaca PDF {file_path.name}: {e}")
    return teks

def read_csv(file_path):
    """Membaca file CSV dan menggabungkan tiap baris menjadi teks."""
    teks = ""
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for baris in csv_reader:
                # Menggabungkan semua kolom menjadi satu kalimat/teks per baris
                row_content = " | ".join([f"{col}: {val}" for col, val in baris.items()])
                teks += f"{row_content}\n"
    except Exception as e:
        print(f"Gagal membaca CSV {file_path.name}: {e}")
    return teks

def chunk_text(text, size=500, overlap=50):
    """Memotong teks panjang menjadi chunk-chunk kecil."""
    potongan = []
    mulai = 0
    while mulai < len(text):
        selesai = mulai + size
        chunk = text[mulai:selesai]
        
        # Simpan chunk jika panjangnya memadai
        if len(chunk) > 50: 
            potongan.append(chunk)
            
        mulai = selesai - overlap
    return potongan