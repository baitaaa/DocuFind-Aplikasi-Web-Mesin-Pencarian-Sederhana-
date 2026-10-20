import os
import time
import requests
import pandas as pd

URL = "https://api.openalex.org/works"

# API key: isi di sini ATAU pakai environment variable OPENALEX_API_KEY
API_KEY = os.getenv("OPENALEX_API_KEY") or "ISI_API_KEY_KAMU_DI_SINI"
EMAIL = "emailkamu@gmail.com"   # dipakai kalau API key tidak diisi

TARGET_TOTAL = 1000
PER_TOPIK = 250

# Urutan: dari yang paling spesifik -> paling umum
TOPIK = {
    "T1_game_2d_platformer_informatika": [
        "2D platformer educational game",
        "web-based educational game informatics learning",
        "game edukasi 2D platformer informatika",
        "educational platformer game",
        "educational game computer science learning",
        "game-based learning programming",
        "serious game education",
        "educational game development",
    ],
    "T2_game_pembelajaran_phaser3": [
        "Phaser 3 game",
        "Phaser game-based learning web",
        "game pembelajaran berbasis web Phaser",
        "HTML5 game educational",
        "web-based game learning media",
        "JavaScript game development learning",
        "game based learning web",
        "learning media game development",
    ],
    "T3_smart_assistant_pattern_matching": [
        "pattern matching chatbot education",
        "cosine similarity chatbot question answering students",
        "chatbot pembelajaran SMK pattern matching",
        "web-based smart assistant learning",
        "educational chatbot",
        "chatbot education students",
        "text similarity question answering",
        "virtual assistant learning vocational school",
    ],
    "T4_ai_debugging_tutor": [
        "AI debugging tutor programming education",
        "intelligent tutoring system programming debugging",
        "tutor debugging pemrograman web siswa SMK",
        "LLM programming assistant novice debugging",
        "programming tutor feedback students",
        "intelligent tutoring system programming",
        "web programming learning problem solving",
        "artificial intelligence programming education",
    ],
}

# Cadangan kalau total masih kurang dari 1000
FALLBACK = [
    "educational game",
    "chatbot education",
    "artificial intelligence education",
    "programming education",
    "game-based learning",
    "intelligent tutoring system",
    "learning media web",
    "vocational high school learning",
]


def rekonstruksi_abstrak(inv):
    """OpenAlex menyimpan abstrak sebagai inverted index; ubah jadi teks."""
    if not inv:
        return ""
    kata = {}
    for w, posisi in inv.items():
        for p in posisi:
            kata[p] = w
    return " ".join(kata[i] for i in sorted(kata))


def cari(query, max_hasil=1000):
    hasil, page = [], 1
    while len(hasil) < max_hasil:
        params = {
            "search": query,
            "filter": "has_abstract:true",
            "per-page": 100,
            "page": page,
        }
        if API_KEY and not API_KEY.startswith("ISI_"):
            params["api_key"] = API_KEY
        else:
            params["mailto"] = EMAIL

        r = None
        for percobaan in range(5):
            try:
                r = requests.get(URL, params=params, timeout=60)
                if r.status_code == 429:
                    print("  Dibatasi API, menunggu...")
                    time.sleep(10 * (percobaan + 1))
                    r = None
                    continue
                if r.status_code in (401, 403):
                    print("  Error autentikasi. Cek API key kamu:", r.text[:200])
                    return hasil
                r.raise_for_status()
                break
            except requests.RequestException as e:
                print("  Kesalahan:", e)
                r = None
                time.sleep(5 * (percobaan + 1))
        if r is None:
            break

        works = r.json().get("results", [])
        if not works:
            break

        for w in works:
            title = (w.get("display_name") or "").strip()
            abstract = rekonstruksi_abstrak(w.get("abstract_inverted_index")).strip()
            if len(title) < 5 or len(abstract) < 100:
                continue
            hasil.append({
                "paper_id": w.get("id"),
                "title": title,
                "abstract": abstract,
                "year": w.get("publication_year"),
                "url": w.get("doi") or w.get("id"),
                "source_query": query,
            })
        page += 1
        time.sleep(0.3)

    print(f"  '{query}': {len(hasil)} dokumen")
    return hasil[:max_hasil]


terpilih, seen_id, seen_title = [], set(), set()


def tambah(d, topik):
    judul = d["title"].casefold().strip()
    if d["paper_id"] in seen_id or judul in seen_title:
        return False
    seen_id.add(d["paper_id"])
    seen_title.add(judul)
    d["topik"] = topik
    terpilih.append(d)
    return True


# Tahap 1: isi kuota tiap topik (spesifik -> umum)
for nama, queries in TOPIK.items():
    print(f"\n=== {nama} ===")
    jumlah = 0
    for q in queries:
        if jumlah >= PER_TOPIK:
            break
        for d in cari(q, max_hasil=600):
            if jumlah >= PER_TOPIK:
                break
            if tambah(d, nama):
                jumlah += 1
    print(f"Terambil {jumlah} untuk {nama}")

# Tahap 2: kalau belum 1000, isi dari query cadangan
if len(terpilih) < TARGET_TOTAL:
    print("\n=== Mengisi kekurangan dari FALLBACK ===")
    for q in FALLBACK:
        if len(terpilih) >= TARGET_TOTAL:
            break
        for d in cari(q, max_hasil=1000):
            if len(terpilih) >= TARGET_TOTAL:
                break
            tambah(d, "FALLBACK")

# Simpan
df = pd.DataFrame(terpilih).head(TARGET_TOTAL)
df.insert(0, "id", range(1, len(df) + 1))

output_path = r"C:\Users\amaliya\Downloads\dataset_1000.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\nJumlah dokumen unik:", len(df))
print(df["topik"].value_counts())
print("File tersimpan di:", output_path)