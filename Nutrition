import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

# 1. Konfigurace
st.set_page_config(page_title="Nutriční Inteligence (MVP)", layout="mobile")
st.title("🍎 Nutriční AI Kouč")

# API Klíč (Google Gemini nebo OpenAI)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. Vstup: Fotka jídla
uploaded_file = st.file_uploader("Vyfoť jídlo", type=["jpg", "jpeg", "png"])
user_context = st.text_input("Jak se cítíš / Kolik máš naspáno?", "Cítím se unavený, spal jsem 5h.")

# 3. Zpracování (The Brain)
if uploaded_file is not None and st.button("Analyzovat"):
    image = Image.open(uploaded_file)
    st.image(image, caption='Tvoje jídlo', use_column_width=True)

    with st.spinner('AI Dietolog přemýšlí...'):
        # Prompt pro Vision Model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
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
        
        response = model.generate_content([prompt, image])
        
        # 4. Výstup
        st.markdown(response.text)
        
        # Tlačítko pro uložení do "databáze" (session state)
        st.success("Zalogováno do deníku.")
