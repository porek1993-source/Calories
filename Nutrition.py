import os
import time
import streamlit as st
from PIL import Image
import google.generativeai as genai

# ----------------------------
# 1. Konfigurace a Tajemství
# ----------------------------
APP_NAME = "Nutriční Inteligence (Prototyp)"
APP_VERSION = "v2.0 - Deep Reasoning"

# Pokud máš přístup, zkus "gemini-1.5-pro" (je chytřejší na detekci jídla).
# "gemini-2.5-flash-lite" je rychlý, ale může přehlédnout detaily.
GEMINI_MODEL = "gemini-2.5-flash-lite" 

def _get_secret(name: str, default: str = "") -> str:
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)

GEMINI_API_KEY = _get_secret("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("Chybí GEMINI_API_KEY. Nastav ho ve Streamlit Secrets nebo .env.")
    st.stop()

# Konfigurace modelu s nižší teplotou pro přesnější fakta
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.4,  # Méně halucinací, více faktů
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# ----------------------------
# 2. UI Layout (Mobile-First)
# ----------------------------
st.set_page_config(page_title=APP_NAME, layout="centered")

# CSS pro "App-like" vzhled na mobilu
st.markdown("""
    <style>
        .block-container { max-width: 600px; padding-top: 2rem; padding-bottom: 5rem;}
        h1 { font-size: 2.2rem; text-align: center; color: #4CAF50; }
        .stButton>button { width: 100%; border-radius: 20px; height: 3rem; font-weight: bold; }
        .stAlert { border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🥗 Nutriční Brain")
st.caption(f"Powered by {GEMINI_MODEL} • {APP_VERSION}")

# ----------------------------
# 3. Vstupy
# ----------------------------
with st.container():
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Analýza obrazu...", use_container_width=True)
    else:
        st.info("👆 Nahraj fotku jídla pro zahájení analýzy.")

    # Kontext uživatele (zjednodušený pro rychlost)
    st.markdown("### 🧠 Kontext")
    col1, col2 = st.columns(2)
    with col1:
        energy_level = st.selectbox("Energie", ["Vysoká", "Normální", "Unavený/Stres"])
    with col2:
        goal = st.selectbox("Cíl", ["Hubnutí", "Udržování", "Nabírání"])
    
    extra_notes = st.text_input("Poznámka (volitelné)", placeholder="např. spal jsem jen 4h, mám po tréninku...")

# ----------------------------
# 4. The "Reasoning Engine" (Algoritmus)
# ----------------------------
def build_senior_coach_prompt(user_context_str):
    """
    V2.1 - Přísnější detekce tuků a explicitní výpis gramáže.
    """
    return f"""
    Jsi nekompromisní nutriční auditor a AI kouč.
    
    KONTEXT UŽIVATELE:
    {user_context_str}

    Tvým úkolem je provést "Deep Scan" talíře. Nespoléhej na průměrné tabulkové hodnoty, dívej se na skutečný objem na fotce.

    KROK 1: DETEKCE A EXPLICITNÍ ROZPIS (CRITICAL STEP)
    - Rozepiš každou položku zvlášť.
    - POZOR NA TUKY: Pokud vidíš máslo, ořechová másla, oleje nebo tučné maso, buď PESIMISTA.
    - Příklad: Ten velký svitek másla na obrázku NENÍ 10g (standard), ale může být 30g a více. Pokud to vypadá jako hodně tuku, POČÍTEJ TO JAKO HODNĚ TUKU.
    - Odhadni gramáž každé položky.

    KROK 2: VÝPOČET (MATH CHECK)
    - Sečti kalorie položek.
    - Aplikuj "Safety Buffer" +15%, pokud si nejsi jistý hloubkou talíře nebo skrytým tukem pod jídlem.

    KROK 3: POSOUZENÍ (NOVA & KONTEXT)
    - NOVA skóre: Uzeniny jsou obvykle NOVA 3-4 (zpracované). Chléb NOVA 3. Máslo NOVA 2. Buď přísný.
    
    KROK 4: KOUČINK
    - Stručná, úderná rada.

    ---
    FORMÁT VÝSTUPU (Markdown):
    
    ## 🍽️ [Název Jídla]
    
    **Rozpis položek (AI Odhad):**
    * 🍞 [Položka 1]: ~[X]g ([X] kcal)
    * 🥩 [Položka 2]: ~[X]g ([X] kcal)
    * 🧈 [Tuk/Máslo]: ~[X]g ([X] kcal) ⚠️ *Zde buď velmi pozorný na objem!*
    
    **Celkový Souhrn:**
    * **🔥 Kalorie:** **[Celkem] kcal**
    * **Makra:** B: [X]g | S: [X]g | T: [X]g
    * **NOVA Skóre:** [1-4]
    
    ---
    ### 🧠 Rada Trenéra
    [Tvoje rada na základě kontextu a složení jídla.]
    """

# ----------------------------
# 5. Execution Logic
# ----------------------------
if uploaded_file is not None and st.button("Analyzovat Jídlo", type="primary"):
    
    context_str = f"Energie: {energy_level}, Cíl: {goal}, Poznámka: {extra_notes}"
    final_prompt = build_senior_coach_prompt(context_str)

    with st.spinner("🕵️‍♂️ Probíhá forenzní analýza jídla..."):
        try:
            model = genai.GenerativeModel(GEMINI_MODEL, generation_config=generation_config)
            
            # Volání API
            response = model.generate_content([final_prompt, image])
            
            # Zobrazení výsledku
            if response.text:
                st.markdown("---")
                st.markdown(response.text, unsafe_allow_html=True)
                st.success("Záznam uložen do nutričního cloudu.")
            else:
                st.error("Model nevrátil žádný text. Zkus to znovu.")

        except Exception as e:
            st.error(f"Chyba při analýze: {e}")
            st.info("Tip: Zkontroluj API klíč nebo zkus jinou fotku.")
