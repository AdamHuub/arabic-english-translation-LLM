import sys
from translation.gemini_api import GeminiTranslator
from config import DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG

def run_test():
    """
    Script de test interactif pour le moteur de traduction Rayya.AI.
    Permet de valider la logique de l'API sans lancer l'interface web.
    """
    translator = GeminiTranslator()
    
    print("\n" + "="*40)
    print(" RAYYA.AI - TRANSLATION ENGINE TEST")
    print("="*40)
    
    # Choix du sens de traduction
    print(f"1. {DEFAULT_SOURCE_LANG} -> {DEFAULT_TARGET_LANG} (Standard)")
    print(f"2. {DEFAULT_TARGET_LANG} -> {DEFAULT_SOURCE_LANG}")
    choice = input("Choisissez le sens (1 par défaut) : ")
    
    source = DEFAULT_SOURCE_LANG if choice != "2" else DEFAULT_TARGET_LANG
    target = DEFAULT_TARGET_LANG if choice != "2" else DEFAULT_SOURCE_LANG
    
    print(f"\nConfiguration active : {source} ---> {target}")
    text = input("Entrez le texte scientifique à traduire: ")
    
    if not text.strip():
        print("Fin du test.")
        return

    print("\n[INFO] Traduction scientifique en cours...")
    result = translator.translate_text(text, source, target, mode="scientific")
    
    print("\n" + "-"*40)
    print("RÉSULTAT DE LA TRADUCTION :")
    print("-"*40)
    print(result)
    print("-"*40 + "\n")

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\nTest arrêté par l'utilisateur.")
    except Exception as e:
        print(f"\n[ERREUR] Une erreur est survenue lors du test : {e}")
