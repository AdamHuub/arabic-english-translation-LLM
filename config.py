import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# --- CONFIGURATION API ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# --- PARAMÈTRES DE TRADUCTION ---
DEFAULT_SOURCE_LANG = "English"
DEFAULT_TARGET_LANG = "Arabic"

# --- RESSOURCES NLTK ---
NLTK_RESOURCES = ["punkt"]

# --- GESTION DES ERREURS ---
if not API_KEY:
    print("ATTENTION : GEMINI_API_KEY non trouvée dans le fichier .env")
