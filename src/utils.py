import re
from io import BytesIO
from typing import List, Dict
import PyPDF2
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Ensure NLTK stopwords are available (first run in new env may download)
try:
    stopwords.words('english')
except:
    import nltk
    nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

def extract_text_from_file(uploaded_file) -> str:
    """Extract text from an uploaded file (PDF or TXT)."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    if name.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(BytesIO(data))
            text = []
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    text.append(txt)
            return "\\n".join(text)
        except Exception as e:
            # Fallback: try decode as text
            try:
                return data.decode('utf-8', errors='ignore')
            except:
                return ""
    elif name.endswith(".txt"):
        return data.decode('utf-8', errors='ignore')
    else:
        # Try decode as text
        try:
            return data.decode('utf-8', errors='ignore')
        except:
            return ""

def clean_text(t: str) -> str:
    t = str(t)
    t = t.replace("\n"," ").lower()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    tokens = [w for w in t.split() if w not in STOPWORDS and len(w)>1]
    return " ".join(tokens)

def compute_similarity_scores(jd_text: str, resumes: List[Dict], topn:int=5) -> List[Dict]:
    """
    Compute TF-IDF vectors for JD and resumes, compute cosine similarity,
    and return ranked results with simple summary.
    """
    docs = [jd_text] + [r["text"] for r in resumes]
    cleaned = [clean_text(d) for d in docs]
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(cleaned)
    jd_vec = X[0].toarray()[0]
    results = []
    for i, r in enumerate(resumes, start=1):
        vec = X[i].toarray()[0]
        # cosine similarity
        denom = (np.linalg.norm(jd_vec) * np.linalg.norm(vec))
        score = float(np.dot(jd_vec, vec) / denom) if denom != 0 else 0.0
        summary = r["text"][:500].replace("\n"," ")
        results.append({
            "rank": None,
            "filename": r["filename"],
            "score": score,
            "summary": summary,
            "text": r["text"]
        })
    # sort by score desc and assign ranks
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    for idx, item in enumerate(results, start=1):
        item["rank"] = idx
    return results

def top_keyword_matches(jd_text: str, resume_text: str, topn:int=5) -> List[str]:
    """Return top matching keywords between JD and resume using simple TF-IDF importance."""
    jd_clean = clean_text(jd_text)
    res_clean = clean_text(resume_text)
    jd_tokens = set(jd_clean.split())
    res_tokens = res_clean.split()
    # frequency in resume
    freq = {}
    for t in res_tokens:
        if t in jd_tokens:
            freq[t] = freq.get(t,0) + 1
    # sort by freq
    items = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:topn]
    return [k for k,v in items]