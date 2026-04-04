import os
import google.generativeai as genai
from dotenv import load_dotenv
from translation.prompts import get_prompt
import urllib.request
import urllib.parse
import json

# --- INITIALISATION ---
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Clé API introuvable. Veuillez configurer GEMINI_API_KEY dans un fichier .env.")

# Configurer l'API Gemini
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

# --- FONCTIONS ---

def fast_google_translate(text, source_lang):
    """
    Bypass ultra-rapide sans LLM (0.1s de latence au lieu de 2s) pour les petits mots simples.
    """
    sl = "en" if source_lang.lower() == "english" else "ar"
    tl = "ar" if source_lang.lower() == "english" else "en"
    
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={urllib.parse.quote(text.strip())}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=3)
        result = json.loads(response.read().decode("utf-8"))
        return "".join([x[0] for x in result[0] if x[0]])
    except Exception:
        return None

def is_simple_bypass(text):
    """Vérifie si le texte est très court (<= 4 mots) et ne nécessite pas un LLM lourd."""
    return len(text.strip().split()) <= 4

def translate_text(text, source_lang, target_lang, prompt_type="detailed"):
    # HYBRID ROUTER : Bypass Gemini API for simple words/phrases!
    if is_simple_bypass(text):
        fast_result = fast_google_translate(text, source_lang)
        if fast_result:
            return fast_result

    direction = "EN→AR" if source_lang.lower() == 'english' else "AR→EN"
    try:
        prompt = get_prompt(prompt_type, text.strip(), direction=direction)
    except ValueError:
        prompt = get_prompt("detailed", text.strip(), direction=direction)

    try:
        config = genai.types.GenerationConfig(temperature=0.1)
        response = model.generate_content(prompt, generation_config=config)
        return response.text.strip()
    except Exception as e:
        return f"Erreur lors de la communication avec l'API Gemini : {e}"

def translate_text_stream(text, source_lang, target_lang, prompt_type="detailed"):
    """
    Traduit un texte en utilisant l'API Gemini et retourne un Stream (générateur).
    Ceci permet un affichage en temps réel côté frontend.
    """
    # HYBRID ROUTER : Bypass Gemini API latency completely for small phrases < 4 words
    if is_simple_bypass(text):
        fast_result = fast_google_translate(text, source_lang)
        if fast_result:
            yield fast_result
            return

    direction = "EN→AR" if source_lang.lower() == 'english' else "AR→EN"
    try:
        prompt = get_prompt(prompt_type, text.strip(), direction=direction)
    except ValueError:
        prompt = get_prompt("detailed", text.strip(), direction=direction)

    config = genai.types.GenerationConfig(temperature=0.1)
    
    try:
        response = model.generate_content(prompt, generation_config=config, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"[API Error: {e}]"