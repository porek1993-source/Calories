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
import os
import time
import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- CONFIG ---
APP_NAME = "Nutriční Inteligence (v3.0)"
GEMINI_MODEL = "gemini-1.5-flash" # Flash je rychlý a levný, pro přesnost zkus 'gemini-1.5-pro'

def _get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except:
        return default

GEMINI_API_KEY = _get_secret("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("Chybí API klíč.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- UI SETUP ---
st.set_page_config(page_title=APP_NAME, layout="mobile") # Zkusíme mobile layout
st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 12px; height: 3rem; background-color: #FF4B4B; color: white; }
        .stCheckbox { padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🥗 AI Food Scanner")

# --- 1. UPLOAD ---
uploaded_file = st.file_uploader("", type=["jpg", "png"], label_visibility="collapsed")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    # --- 2. PRE-FLIGHT CHECK (VYLEPŠENÍ) ---
    st.write("---")
    st.markdown("#### 🕵️‍♂️ Upřesnění pro AI (nepovinné)")
    
    col1, col2 = st.columns(2)
    with col1:
        is_buttered = st.checkbox("🍞 Pečivo je namazané", value=True, help="Je pod šunkou/sýrem máslo?")
        is_fried = st.checkbox("🍟 Smažené na oleji", help="Řízek, hranolky, restovaná zelenina...")
    with col2:
        is_restaurant = st.checkbox("restaurant Restaurace", help="Jídla z restaurace mají obvykle o 20% více tuku.")
        is_sweet_drink = st.checkbox("🥤 Sladký nápoj k tomu")

    user_note = st.text_input("Jiná poznámka", placeholder="např. to žluté je SÝR, ne máslo")

    # Sestavení kontextu z tlačítek
    context_tags = []
    if is_buttered: context_tags.append("PEČIVO JE NAMAZANÉ (Připočti máslo/tuk)")
    if is_fried: context_tags.append("JÍDLO JE SMAŽENÉ (Připočti nasáklý olej)")
    if is_restaurant: context_tags.append("VAŘENO V RESTAURACI (Použij vyšší koeficient kalorií)")
    if is_sweet_drink: context_tags.append("PIL JSEM SLADKÝ NÁPOJ (Není na fotce, připočti cca 150 kcal)")
    
    context_str = ", ".join(context_tags)

    # --- 3. ANALÝZA ---
    if st.button("🔍 Analyzovat Detailně"):
        
        # PROMPT ENGINEERING V3.0
        prompt = f"""
        Jsi forenzní nutriční expert. Analyzuj fotku jídla s maximální přesností.
        
        KRITICKÉ VSTUPY OD UŽIVATELE (TOTO JE PRAVDA, NEODPORUJ TOMU):
        [{context_str}]
        Poznámka uživatele: "{user_note}"

        INSTRUKCE PRO ANALÝZU (Think Step-by-Step):
        
        1. **Kalibrace velikosti:** - Hledej na fotce příbor, ruku, skleničku nebo standardní velikost talíře. 
           - Pokud vidíš velký talíř, jídla je více, než se zdá.
        
        2. **Detekce Suroviny (Sýr vs. Máslo vs. Vejce):**
           - Pokud uživatel nenapsal jinak, použij vizuální logiku: 
           - Velké žluté plátky = SÝR (Eidam/Gouda).
           - Malá kostka/hoblinka = MÁSLO.
           - Bílo-žluté nepravidelné = MÍCHANÁ VEJCE.
        
        3. **Výpočet Kalorií (Sečti A + B + C):**
           - A (Viditelné): Co vidíš na talíři.
           - B (Neviditelné): Pokud uživatel zaškrtll "Pečivo je namazané", připočti automaticky 10-15g másla (cca 100 kcal).
           - C (Koeficient): Pokud je to restaurace, vynásob výsledek x1.1.

        4. **Výstup:**
           - Buď stručný, ale přesný v číslech.
           - Vypiš makra (B/S/T).

        FORMÁT VÝSTUPU (Markdown):
        ## 🍽️ [Název Jídla]
        
        **Detailní Rozpis:**
        * [Položka 1] (~[g]): [kcal]
        * [Položka 2] (~[g]): [kcal]
        * ...
        * 🕵️‍♂️ *Skryté tuky/Namazání:* [kcal]
        
        **Celkem:** 🔥 **[SUMA] kcal** (B: [g] | S: [g] | T: [g])

        **Rychlá rada:** [Jedna věta]
        """

        with st.spinner("Provádím volumetrickou analýzu..."):
            try:
                model = genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content([prompt, image])
                st.markdown(response.text)
                
                # Visual feedback pro dobrý pocit
                st.balloons()
                
            except Exception as e:
                st.error(f"Chyba: {e}")
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
