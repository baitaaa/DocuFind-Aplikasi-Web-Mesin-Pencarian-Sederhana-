
import os
import json
import re
import math
from collections import Counter

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "documents.json")


# ==========================================
# 1. MEMUAT DATASET OPENALEX
# ==========================================


# ==========================================
# 1. MEMUAT DATASET OPENALEX
# ==========================================

def load_docs():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Peringatan: format documents.json harus berupa list.")
            return []

        print(f"Berhasil memuat {len(data)} dokumen.")
        return data

    except FileNotFoundError:
        print(f"File dataset tidak ditemukan: {DATA_FILE}")
        return []

    except json.JSONDecodeError as e:
        print(f"Format JSON tidak valid: {e}")
        return []


# ==========================================
# 2. PREPROCESSING TEKS
# ==========================================

def tokenize(text):
    text = (text or "").lower()
    return re.findall(r"[a-zA-Z0-9]+|[^\W\d_]+", text, flags=re.UNICODE)


def preprocess(text):
    stopwords = {
        "the", "and", "for", "with", "from", "that", "this",
        "are", "was", "were", "into", "using", "use", "our",
        "their", "they", "have", "has", "had", "not", "but",
        "can", "will", "its", "of", "in", "on", "at", "to",
        "a", "an", "is", "as", "by", "be", "or", "we", "it",
        "than", "yang", "dan", "di", "ke", "dari", "untuk",
        "dengan", "pada", "adalah", "ini", "itu", "dalam",
        "atau", "sebagai", "oleh", "dapat", "akan", "tidak",
        "lebih"
    }

    return [
        token for token in tokenize(text)
        if len(token) > 1 and token not in stopwords
    ]


# ==========================================
# 3. MENGGABUNGKAN TEKS DOKUMEN
# ==========================================

def doc_text(doc):
    fields = (
        "title",
        "abstract",
        "content",
        "venue",
        "source_query",
        "topik"
    )

    return " ".join(
        str(doc.get(key) or "")
        for key in fields
    )


# ==========================================
# 4. TF-IDF DAN COSINE SIMILARITY
# ==========================================

def rank_documents(query, docs):
    query_terms = preprocess(query)

    if not query_terms or not docs:
        return [], query_terms

    tokenized_docs = [
        preprocess(doc_text(doc))
        for doc in docs
    ]

    total_docs = len(tokenized_docs)
    document_frequency = Counter()

    for tokens in tokenized_docs:
        document_frequency.update(set(tokens))

    idf = {
        term: math.log(
            (total_docs + 1) /
            (document_frequency[term] + 1)
        ) + 1
        for term in document_frequency
    }

    def make_vector(tokens):
        term_frequency = Counter(tokens)

        return {
            term: (1 + math.log(count)) * idf.get(term, 0)
            for term, count in term_frequency.items()
        }

    document_vectors = [
        make_vector(tokens)
        for tokens in tokenized_docs
    ]

    query_frequency = Counter(query_terms)

    query_vector = {
        term: (1 + math.log(count)) *
        idf.get(term, math.log(total_docs + 1) + 1)
        for term, count in query_frequency.items()
    }

    query_norm = math.sqrt(
        sum(value * value for value in query_vector.values())
    ) or 1

    results = []

    for doc, vector in zip(docs, document_vectors):
        dot_product = sum(
            weight * query_vector.get(term, 0)
            for term, weight in vector.items()
        )

        document_norm = math.sqrt(
            sum(value * value for value in vector.values())
        ) or 1

        score = dot_product / (document_norm * query_norm)

        if score > 0:
            item = dict(doc)
            item["score"] = round(score, 6)
            item["matched_terms"] = list(dict.fromkeys(
                term for term in query_terms if term in vector
            ))

            results.append(item)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results, query_terms


# ==========================================
# 5. HALAMAN UTAMA
# ==========================================

@app.route("/")
def index():
    docs = load_docs()

    return render_template(
        "index.html",
        doc_count=len(docs)
    )


# ==========================================
# 6. PENCARIAN DOKUMEN
# ==========================================

@app.route("/search", methods=["POST"])
def search():
    query = (request.form.get("query") or "").strip()
    docs = load_docs()

    if not query:
        return render_template(
            "results.html",
            query="",
            results=[],
            terms=[],
            doc_count=len(docs),
            error="Masukkan kata kunci terlebih dahulu."
        )

    results, terms = rank_documents(query, docs)

    return render_template(
        "results.html",
        query=query,
        results=results[:100],
        terms=terms,
        doc_count=len(docs),
        error=None
    )


# ==========================================
# 7. API PENCARIAN
# ==========================================

@app.route("/api/search", methods=["GET"])
def api_search():
    query = (request.args.get("q") or "").strip()

    if not query:
        return jsonify({
            "error": "Parameter q wajib diisi"
        }), 400

    docs = load_docs()
    results, terms = rank_documents(query, docs)

    return jsonify({
        "query": query,
        "processed_terms": terms,
        "documents_indexed": len(docs),
        "results": results[:100]
    })


# ==========================================
# 8. DAFTAR DOKUMEN
# ==========================================

@app.route("/documents")
def documents():
    docs = load_docs()

    return render_template(
        "documents.html",
        docs=docs,
        doc_count=len(docs)
    )


# ==========================================
# 9. STATUS APLIKASI
# ==========================================

@app.route("/health")
def health():
    docs = load_docs()

    return jsonify({
        "status": "ok",
        "data_source": "OpenAlex",
        "documents_indexed": len(docs)
    })


if __name__ == "__main__":
    app.run(debug=True)
