import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Choix du fournisseur d'IA : "gemini" ou "groq"
AI_PROVIDER = "gemini"

# Configuration API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Configuration API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Configuration des langues par défaut
DEFAULT_SOURCE_LANG = "arabe"
DEFAULT_TARGET_LANG = "anglais"
