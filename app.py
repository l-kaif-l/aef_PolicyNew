
# app.py
import os, io, re, time
from typing import List, Dict
import streamlit as st
from docx import Document
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import AzureOpenAI

# ================== PAGE ==================
st.set_page_config(page_title="KII Coder (Plain Text)", layout="wide")
st.title("📝 KII Transcript → Thematic Coding (Plain Text)")

st.markdown("""
Upload one or more **KII transcripts** (.docx or .txt).  
The app classifies each segment into your **KII codebook** and returns **plain text** blocks:

Theme: ...
Subcodes: ...
Insight: ...
Quote: "..."


You can read on-screen and download a TXT per file.
""")

# ================== AZURE CONFIG ==================
# Add these in Streamlit Cloud → App settings → Secrets
# AZURE_OPENAI_API_KEY = "..."
# AZURE_OPENAI_ENDPOINT = "https://<your-resource>.openai.azure.com/"
# AZURE_OPENAI_API_VERSION = "2024-10-21"
# DEPLOYMENT = "gpt-4o"

def init_client():
    try:
        return AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version=st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"].strip()
        ), st.secrets.get("DEPLOYMENT", "gpt-4o")
    except Exception:
        st.error("Missing/invalid Azure secrets. Set them in App settings → Secrets.")
        st.stop()

client, DEPLOYMENT = init_client()

# ================== KII CODEBOOK ==================
KII_TAXONOMY: Dict[str, Dict[str, str]] = {
    "Respondent Background (BCK)": {
        "BCK_Role": "Role of respondent (farmer/CRP/leader).",
        "BCK_Experience": "Years of farming / NF experience."
    },
    "Introduction and Spread of NF (SPR)": {
        "SPR_Introduced_By": "Who introduced NF (CSA/govt/others).",
        "SPR_Response": "Community’s initial reactions.",
        "SPR_EarlyAdopters": "Presence/influence of early adopters."
    },
    "Adoption Patterns (ADO)": {
        "ADO_Numbers": "Adopters initially vs now.",
        "ADO_Types": "Types of farmers adopting (small/marginal/large).",
        "ADO_DropoutReasons": "Reasons for dropping out."
    },
    "NF Practices and Inputs (PRC)": {
        "PRC_BiologicalInputs": "Inputs like FYM/neem/panchagavya.",
        "PRC_InputAccess": "Access/availability of inputs.",
        "PRC_CropTypes": "Crops under NF / cropping changes."
    },
    "Challenges and Barriers (CHL)": {
        "CHL_Labor": "Labor-related constraints.",
        "CHL_Yield": "Yield-related concerns.",
        "CHL_Market": "Market/premium issues.",
        "CHL_Social": "Social stigma/peer pressure.",
        "CHL_HealthFoodChange": "Diet/health change issues."
    },
    "Support Systems (SUP)": {
        "SUP_CSA": "CSA training/demos/CRP support.",
        "SUP_GovtSupport": "Govt schemes/benefits/gaps.",
        "SUP_Suggestions": "Suggestions to improve support."
    },
    "Benefits of NF (BEN)": {
        "BEN_CostReduction": "Reduced input costs.",
        "BEN_SoilHealth": "Soil improvements.",
        "BEN_HumanHealth": "Human health improvements.",
        "BEN_IncomeStability": "Income stability/parity."
    },
    "Ecosystem and Policy (ECO)": {
        "ECO_MarketPolicy": "Price support / exclusive markets.",
        "ECO_EcosystemChange": "System/political leadership asks.",
        "ECO_InstitutionalLink": "Links to govt institutions."
    },
    "Future Direction and Continuity (FUT)": {
        "FUT_ExposureVisits": "Exposure/knowledge sharing.",
        "FUT_TrainingNeed": "Further/refresher training needs.",
        "FUT_Infrastructure": "Storage/input centres/infrastructure."
    }
}

# ================== HELPERS ==================
def read_docx(file) -> str:
    doc = Document(file)
    return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())

def read_txt(file) -> str:
    return file.read().decode("utf-8", errors="ignore")

def segment_text(text: str, max_chars: int = 1800) -> List[str]:
    text = re.sub(r'\r\n?', '\n', text)
    blocks = [b.strip() for b in re.split(r'\n{2,}', text) if b.strip()]
    segs: List[str] = []
    for blk in blocks:
        if len(blk) <= max_chars:
            segs.append(blk)
        else:
            # soft split on sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', blk)
            cur, cur_len = [], 0
            for s in sentences:
                if cur_len + len(s) > max_chars and cur:
                    segs.append(" ".join(cur).strip())
                    cur, cur_len = [], 0
                cur.append(s)
                cur_len += len(s) + 1
            if cur:
                segs.append(" ".join(cur).strip())
    return segs

def taxonomy_lines(tax: Dict[str, Dict[str,str]]) -> str:
    return "\n".join(f"{theme} → {', '.join(subs.keys())}" for theme, subs in tax.items())

def build_prompt(segment: str, tax: Dict[str,Dict[str,str]]) -> str:
    tax_text = taxonomy_lines(tax)
    return f"""
You are a qualitative coding assistant. Classify the KII excerpt into the taxonomy BELOW.
Pick exactly ONE theme and one or more subcodes from THAT theme only.
Then write a short insight and one short verbatim quote from the text (<=25 words).

TAXONOMY:
{tax_text}

TEXT:
\"\"\"{segment}\"\"\"

Return PLAIN TEXT only (no JSON, no backticks), exactly in this format:

Theme: <one theme name exactly as in taxonomy>
Subcodes: <comma-separated subcodes from the chosen theme>
Insight: <one concise, specific sentence>
Quote: "<short verbatim quote from TEXT, <=25 words>"

(Do not add any extra lines or sections.)
""".strip()

@retry(wait=wait_exponential(multiplier=1, min=1, max=20),
       stop=stop_after_attempt(5),
       retry=retry_if_exception_type(Exception))
def call_azure(prompt: str) -> str:
    res = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    return res.choices[0].message.content.strip()

# ================== SIDEBAR ==================
with st.sidebar:
    uploaded_files = st.file_uploader("Upload KII transcripts (.docx / .txt)", type=["docx","txt"], accept_multiple_files=True)
    max_chars = st.slider("Max segment size (chars)", 800, 3000, 1800, 100)
    run = st.button("🚀 Run Coding")

# ================== MAIN ==================
if run and uploaded_files:
    for up in uploaded_files:
        st.write(f"**Processing:** `{up.name}`")
        # read file
        if up.name.lower().endswith(".docx"):
            text = read_docx(up)
        else:
            text = read_txt(up)

        segments = segment_text(text, max_chars=max_chars)

        # build report
        lines = [f"=== KII CODED REPORT — {up.name} ===", ""]
        progress = st.progress(0)
        for i, seg in enumerate(segments, start=1):
            prompt = build_prompt(seg, KII_TAXONOMY)
            try:
                out = call_azure(prompt)
            except Exception as e:
                out = f"Theme: (error)\nSubcodes: \nInsight: Azure error: {e}\nQuote: \"\""

            lines.append(f"[Segment {i}]")
            lines.append(out)
            lines.append("")
            progress.progress(i / max(len(segments), 1))
            time.sleep(0.1)

        report = "\n".join(lines)

        # show & download
        with st.expander(f"📄 Report: {up.name}", expanded=True):
            st.text(report)

        fname_base = os.path.splitext(up.name)[0]
        st.download_button(
            label=f"💾 Download TXT — {fname_base}_KII_CODED.txt",
            data=report.encode("utf-8"),
            file_name=f"{fname_base}_KII_CODED.txt",
            mime="text/plain"
        )

elif run and not uploaded_files:
    st.warning("Please upload at least one file.")
