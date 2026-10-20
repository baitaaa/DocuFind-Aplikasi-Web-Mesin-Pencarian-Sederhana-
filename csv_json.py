
import pandas as pd
import json
import os

# Lokasi CSV hasil pengambilan dari OpenAlex
csv_path = r"C:\Users\amaliya\Downloads\DocuFind_SemanticScholar\DocuFind_SemanticScholar\data\dataset_1000.csv"

# Lokasi documents.json di proyek DocuFind
json_path = os.path.join("data", "documents.json")

# Baca CSV
df = pd.read_csv(csv_path)

# Ubah nilai kosong menjadi string kosong
df = df.fillna("")

# Ubah ke format JSON
documents = df.to_dict(orient="records")

# Pastikan folder data tersedia
os.makedirs("data", exist_ok=True)

# Simpan JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print("Konversi berhasil!")
print("Jumlah dokumen:", len(documents))
print("File tersimpan:", os.path.abspath(json_path))
