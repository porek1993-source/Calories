import os
import time
import streamlit as st
from PIL import Image
import google.generativeai as genai

# ----------------------------
# Helpers
# ----------------------------
def _get_secret(name: str, default: str = "") -> str:
    """
    1) Streamlit Cloud: st.secrets["NAME"]
    2) Lokálně / Docker: env var NAME
    """
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)

# ----------------------------
# Constants
# ----------------------------
APP_NAME = "Nutriční Inteligence (MVP)"
APP_VERSION = "v1.0"

GEMINI_MODEL = "gemini-1.5-pro"  # klidně změň na "gemini-2.5-flash-lite", pokud ho máš povolený
MAX_AI_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ----------------------------
# Streamlit UI config
# ----------------------------
# Streamlit layout umí jen "centered" nebo "wide" (ne "mobile")
st.set_page_config(page_title=f"{APP_NAME} {APP_VERSION}", layout="centered")
st.title("🍎 Nutriční AI Kouč")

# “Mobile feel” (volitelné) – zúží obsah
st.markdown(
    """
    <style>
      .block-container { max-width: 680px; padding-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# API Key + Gemini config
# ----------------------------
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("Chybí GEMINI_API_KEY. Nastav ho ve Streamlit Secrets nebo jako env var.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------
# Inputs
# ----------------------------
uploaded_file = st.file_uploader("Vyfoť jídlo", type=["jpg", "jpeg", "png"])
user_context = st.text_input("Jak se cítíš / Kolik máš naspáno?", "Cítím se unavený, spal jsem 5h.")

# ----------------------------
# Analyze
# ----------------------------
if uploaded_file is not None and st.button("Analyzovat"):
    image = Image.open(uploaded_file)

    st.image(image, caption="Tvoje jídlo", use_container_width=True)

    prompt = f"""
Jsi expert na výživu a psychologii. Analyzuj tento obrázek jídla.

Uživatelův kontext: {user_context}

Úkoly:
1. Identifikuj jídlo (buď specifický, např. 'Svíčková na smetaně', ne jen 'maso s omáčkou').
2. Odhadni kalorie a makra (B/S/T) s tolerancí +/- 20%. Uvažuj "neviditelné kalorie" (olej, cukr).
3. Urči NOVA skóre (stupeň zpracování 1-4).
4. Poskytni radu jako empatický kouč. Pokud je uživatel unavený, nebuď tvrdý.

Výstup formátuj jako Markdown tabulku + text.
"""

    with st.spinner("AI dietolog přemýšlí..."):
        model = genai.GenerativeModel(GEMINI_MODEL)

        last_err = None
        response = None

        for attempt in range(1, MAX_AI_RETRIES + 1):
            try:
                # Vision prompt: text + image
                response = model.generate_content([prompt, image])
                break
            except Exception as e:
                last_err = e
                if attempt < MAX_AI_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)  # jednoduchý backoff
                else:
                    st.error(f"Nepodařilo se zavolat Gemini po {MAX_AI_RETRIES} pokusech.")
                    st.exception(last_err)
                    st.stop()

    # Output
    text = getattr(response, "text", None)
    if not text:
        st.warning("Gemini nevrátilo textový výstup. Zkus jinou fotku nebo model.")
    else:
        st.markdown(text)

    st.success("Zalogováno do deníku.")
