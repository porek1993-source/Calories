import os
import time
import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- CONFIG ---
APP_NAME = "Nutriční Inteligence (v3.0)"
GEMINI_MODEL = "gemini-2.5-flash-lite" # Flash je rychlý a levný, pro přesnost zkus 'gemini-1.5-pro'

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
st.set_page_config(page_title=APP_NAME, layout="centered") # Zkusíme mobile layout
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
