# DocuFind — Search Engine Akademik

DocuFind adalah aplikasi web mesin pencari dokumen akademik berbasis Flask yang memungkinkan pengguna menemukan publikasi ilmiah berdasarkan kata kunci. Sistem menggunakan preprocessing teks, pembobotan TF-IDF, dan metode Vector Space Model (VSM) dengan cosine similarity untuk mengurutkan hasil pencarian berdasarkan relevansi.

Dataset terdiri dari 1.000 dokumen penelitian yang diperoleh dari OpenAlex dan disimpan secara lokal dalam format JSON.

## Fitur

1. **Dashboard pencarian akademik** untuk memasukkan kata kunci dan melihat statistik jumlah dokumen.
2. **Dataset 1.000 dokumen** yang dikumpulkan dari OpenAlex dan dikelompokkan ke dalam empat topik penelitian.
3. **Preprocessing teks**, meliputi normalisasi huruf menjadi huruf kecil, tokenisasi, dan penyaringan stopword.
4. **Pembobotan TF-IDF** untuk menghitung bobot kata pada dokumen dan kueri.
5. **Pemeringkatan dokumen menggunakan VSM** dengan cosine similarity.
6. **Halaman hasil pencarian** yang menampilkan judul, abstrak, tahun publikasi, skor relevansi, dan tautan menuju publikasi jika tersedia.
7. **Endpoint API lokal** untuk pencarian dokumen dan pemeriksaan status korpus.

## Topik Dataset

Dataset dikumpulkan dari OpenAlex berdasarkan empat kelompok topik berikut:

| Kode | Topik |
|---|---|
| T1 | Game 2D platformer untuk pembelajaran Informatika |
| T2 | Game pembelajaran berbasis web dan Phaser 3 |
| T3 | Smart assistant dan pattern matching |
| T4 | AI debugging tutor untuk pembelajaran pemrograman |

Setiap dokumen dapat memiliki informasi berupa ID, paper ID, judul, abstrak, tahun publikasi, URL publikasi, kueri sumber, dan kategori topik.

## Teknologi yang Digunakan

- **Bahasa pemrograman:** Python 3.10 atau lebih baru
- **Backend:** Flask
- **Sumber metadata akademik:** OpenAlex
- **Format dataset:** CSV dan JSON
- **Metode pencarian:** TF-IDF dan Vector Space Model
- **Metode pengukuran relevansi:** Cosine similarity
- **Frontend:** HTML dan CSS dengan template Jinja2

## Struktur Proyek

```text
DocuFind_SemanticScholar/
├── app.py
├── ambildataset.py
├── csv_json.py
├── requirements.txt
├── data/
│   ├── dataset_1000.csv
│   └── documents.json
└── templates/
    ├── base.html
    ├── index.html
    ├── results.html
    └── documents.html
```

Struktur di atas merupakan contoh struktur proyek. Sesuaikan nama file dengan file yang benar-benar tersedia di folder proyek.

## Persyaratan

- Python 3.10 atau lebih baru
- Koneksi internet untuk mengambil dataset dari OpenAlex
- Dependensi Python yang tercantum dalam `requirements.txt`

Koneksi internet tidak diperlukan untuk melakukan pencarian lokal setelah dataset tersedia, kecuali jika aplikasi memiliki fitur lain yang membutuhkan akses internet.

## Menjalankan Aplikasi di Windows

### 1. Buka CMD dan masuk ke folder proyek

```bat
cd /d "C:\Users\amaliya\Downloads\DocuFind_SemanticScholar\DocuFind_SemanticScholar"
```

### 2. Buat virtual environment

```bat
py -m venv .venv
```

Aktifkan virtual environment:

```bat
.venv\Scripts\activate
```

### 3. Instal dependensi

```bat
python -m pip install -r requirements.txt
```

### 4. Jalankan aplikasi

```bat
python app.py
```

Buka alamat berikut di browser:

http://127.0.0.1:5000/

## Proses Pengumpulan dan Konversi Dataset

Proses penyediaan dataset dilakukan melalui tahapan berikut:

1. Menjalankan `ambildataset.py` untuk mengambil metadata publikasi dari OpenAlex berdasarkan empat kelompok topik penelitian.
2. Menggabungkan hasil pengumpulan menjadi satu dataset CSV dengan target 1.000 dokumen.
3. Menjalankan `csv_json.py` untuk mengonversi dataset CSV menjadi format JSON.
4. Menyimpan hasil konversi ke `data/documents.json`.
5. Memuat dataset JSON pada aplikasi Flask untuk digunakan dalam proses pencarian lokal.

Untuk mengonversi dataset, jalankan:

```bat
python csv_json.py
```

Pastikan file CSV sumber tersedia di lokasi yang ditentukan dalam `csv_json.py`. Setelah konversi, periksa jumlah dokumen yang tersimpan di `data/documents.json`.

## Endpoint API Lokal

| Endpoint | Fungsi |
|---|---|
| `GET /health` | Memeriksa status aplikasi dan jumlah dokumen yang terbaca |
| `GET /api/search?q=machine%20learning` | Melakukan pencarian lokal berdasarkan kata kunci |
| `GET /documents` | Menampilkan daftar dokumen yang tersimpan |

Contoh respons endpoint `/health`:

```json
{
  "status": "ok",
  "data_source": "OpenAlex",
  "documents_indexed": 1000
}
```

Nilai `documents_indexed` menunjukkan jumlah dokumen yang berhasil dibaca aplikasi, bukan sekadar jumlah dokumen yang pernah dikumpulkan.

## Metode Pencarian

### 1. Preprocessing

Teks kueri dan dokumen diproses melalui normalisasi huruf, tokenisasi, serta penyaringan stopword sederhana. Tahap ini membantu menyederhanakan teks sebelum pembobotan.

### 2. TF-IDF

Sistem menggunakan pembobotan term frequency dan inverse document frequency. Formula yang digunakan adalah:

- TF berbobot: `1 + log(tf)`
- IDF: `log((N + 1) / (df + 1)) + 1`

Keterangan:

- `tf` adalah frekuensi suatu kata dalam dokumen.
- `N` adalah jumlah dokumen dalam korpus.
- `df` adalah jumlah dokumen yang mengandung kata tersebut.

### 3. Vector Space Model dan Cosine Similarity

Kueri dan dokumen direpresentasikan sebagai vektor berbobot TF-IDF. Cosine similarity digunakan untuk menghitung kemiripan antara vektor kueri dan vektor dokumen.

Dokumen dengan skor kemiripan lebih tinggi ditempatkan pada posisi lebih atas dalam hasil pencarian.

## Catatan Metodologi

- Dataset bersumber dari OpenAlex dan disimpan secara lokal dalam format JSON.
- Kualitas hasil pencarian bergantung pada kelengkapan metadata, judul, abstrak, dan kesesuaian kata kunci.
- Sebagian publikasi mungkin tidak menyediakan abstrak atau tautan publikasi yang dapat diakses.
- Daftar stopword pada aplikasi masih sederhana dan dapat dikembangkan sesuai bahasa dalam korpus.
- Stemming atau lemmatisasi dapat dipertimbangkan sebagai pengembangan lebih lanjut.
- Jumlah dokumen yang berhasil dimuat perlu diverifikasi melalui endpoint `/health` atau statistik dashboard.
- Skor cosine similarity digunakan untuk mengurutkan relevansi berdasarkan representasi TF-IDF, bukan sebagai ukuran langsung kualitas ilmiah publikasi.

## Pengembangan Selanjutnya

DocuFind dapat dikembangkan dengan penambahan filter tahun publikasi, kategori topik, pagination, stemming bahasa Indonesia, serta evaluasi kualitas pencarian menggunakan metrik seperti Precision@K, Recall@K, dan Mean Average Precision (MAP).

---

**DocuFind — Academic Document Search Engine**

Mesin pencari dokumen akademik berbasis Flask dengan dataset OpenAlex, TF-IDF, dan Vector Space Model.
