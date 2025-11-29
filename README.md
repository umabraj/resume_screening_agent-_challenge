# AI Resume Screening & Candidate Ranking Agent — MVP

This is a minimal, **local** Resume Screening Agent built for quick demonstration and the Rooman 48-hour challenge.
It ranks uploaded resumes against a job description using TF-IDF similarity (no external API keys required).

## Features (MVP)
- Paste job description or upload a `.txt` JD.
- Upload multiple resumes (PDF or TXT).
- Computes TF-IDF similarity and ranks candidates.
- Shows top keyword matches and a short summary.
- Download ranked results as CSV.

## Tech stack
- Python, Streamlit
- scikit-learn (TfidfVectorizer)
- PyPDF2 for PDF text extraction
- NLTK stopwords

## Run locally (recommended)
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\\Scripts\\activate    # Windows
```
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
streamlit run app.py
```

## Notes
- This MVP uses TF-IDF for speed and simplicity. For production, replace TF-IDF with embedding models (OpenAI, sentence-transformers) and a vector DB (FAISS/Chroma).
- Sample resumes and a sample JD are included in `sample_resumes/`.

## Files in repo
- `app.py` — Streamlit frontend
- `src/utils.py` — text extraction, cleaning, scoring helpers
- `requirements.txt`
- `sample_resumes/` — sample txt resumes and jd