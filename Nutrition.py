import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import os
import io

def get_secret(name: str, default: str = "") -> str:
    # Streamlit Cloud: st.secrets["..."] / lokálně: env var
    return st.secrets.get(name, os.getenv(name, default))

# 1. Konfigurace (Streamlit má layout jen "centered" nebo "wide")
st.set_page_config(page_title="Nutriční Inteligence (MVP)", layout="centered")
st.title("🍎 Nutriční AI Kouč")

API_KEY = get_secret("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("Chybí GEMINI_API_KEY (Streamlit Secrets nebo env var).")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 2. Vstup
uploaded_file = st.file_uploader("Vyfoť jídlo", type=["jpg", "jpeg", "png"])
user_context = st.text_input("Jak se cítíš / Kolik máš naspáno?", "Cítím se unavený, spal jsem 5h.")

# 3. Zpracování
if uploaded_file is not None and st.button("Analyzovat"):
    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/jpeg"

    # zobraz náhled
    image_preview = Image.open(io.BytesIO(image_bytes))
    st.image(image_preview, caption="Tvoje jídlo", use_container_width=True)

    img_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

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
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # klidně změň na vyšší (např. 2.5 pro), pokud chceš kvalitu
            contents=[img_part, prompt],
        )

    st.markdown(response.text)
    st.success("Zalogováno do deníku.")
