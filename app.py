import streamlit as st
import pandas as pd
import base64
from src.utils import extract_text_from_file, compute_similarity_scores, top_keyword_matches

# ----- Page Setup -----
st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="🤖",
    layout="wide",
)

# ----- Header -----
st.markdown(
    """
    <h1 style='text-align:center; color:#4B8BBE;'>🤖 AI Resume Screening & Candidate Ranking</h1>
    <p style='text-align:center; font-size:18px; color:gray;'>
        Upload a Job Description and multiple resumes.  
        The system ranks candidates using TF-IDF similarity scoring.
    </p>
    """,
    unsafe_allow_html=True,
)

# ----- Instructions -----
with st.expander("📘 How It Works"):
    st.markdown("""
    **1️⃣ Paste the Job Description** or upload a `.txt` file  
    **2️⃣ Upload Resumes** (PDF or TXT — multiple resumes allowed)  
    **3️⃣ Click _Run Screening_**  
    **4️⃣ View Ranked Candidates** with:  
    - Similarity Score  
    - Top keyword matches  
    - Short extracted summary  
    **5️⃣ Download results (CSV)**  
    """)

st.markdown("---")

# ----- Input Section -----
col1, col2 = st.columns(2)

with col1:
    jd_text = st.text_area("📄 Paste Job Description", height=230)

with col2:
    jd_file = st.file_uploader("Or Upload Job Description (.txt)", type=["txt"])
    if jd_file:
        jd_text = jd_file.getvalue().decode("utf-8")

st.markdown("---")

uploaded_files = st.file_uploader(
    " Upload Resumes (PDF / TXT) — Multiple Allowed",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

# ----- Run Screening -----
if st.button(" Run Screening", use_container_width=True):

    if not jd_text or len(jd_text.strip()) < 10:
        st.error("⚠️ Please provide a Job Description.")
        st.stop()

    if not uploaded_files:
        st.error("⚠️ Please upload at least one resume.")
        st.stop()

    st.success("⏳ Processing resumes... Please wait.")

    resumes = []
    for f in uploaded_files:
        try:
            text = extract_text_from_file(f)
        except Exception as e:
            st.warning(f" Couldn't extract text from {f.name}: {e}")
            text = ""

        resumes.append({"filename": f.name, "text": text})

    # Compute similarity
    results = compute_similarity_scores(jd_text, resumes)

    # Top keywords
    for r in results:
        r["top_matches"] = ", ".join(top_keyword_matches(jd_text, r["text"], topn=5))

    df = pd.DataFrame(results)
    df_display = df[["rank", "filename", "score", "top_matches", "summary"]]

    # ----- Display Table -----
    st.subheader("🏆 Ranked Candidates")
    st.dataframe(df_display.style.highlight_max("score", color="lightgreen"), height=300)

    # ----- CSV Download -----
    csv = df_display.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f"""
    <a href='data:file/csv;base64,{b64}' download='ranked_results.csv'
       style='padding:10px 20px; background:#4B8BBE; color:white; border-radius:8px;
       text-decoration:none; font-size:18px;'>
        Download ranked_results.csv
    </a>
    """
    st.markdown(href, unsafe_allow_html=True)

    # ----- Detailed Candidate Breakdown -----
    st.markdown("### 👤 Candidate Details (Auto-Generated)")
    for _, row in df.sort_values("rank").iterrows():
        st.markdown(
            f"""
            <div style="padding:15px; border:1px solid #d9d9d9; border-radius:10px; margin-bottom:15px;">
                <h4>#{int(row['rank'])} — {row['filename']}</h4>
                <b>Similarity Score:</b> {row['score']:.4f}<br>
                <b>Top Keyword Matches:</b> {row['top_matches']}<br>
                <b>Summary:</b> {row['summary'][:250]}...
            </div>
            """,
            unsafe_allow_html=True,
        )
