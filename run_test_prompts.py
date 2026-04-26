import os
import sys
import time

# Ajout du chemin racine pour l'import
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)

from translation.gemini_api import _translator as translator

def run_test():
    input_file = os.path.join(root, "data", "raw", "english_texts.txt")
    output_file = os.path.join(root, "res")
    
    if not os.path.exists(input_file):
        print(f"Erreur: {input_file} introuvable")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        # On lit tout le texte d'un coup comme demandé
        full_text = f.read().strip()

    prompts_to_test = ["V5", "V7", "V9"]
    labels = {"V9": "ULTRA MAX", "V5": "pro", "V7": "standard"}
    
    results = []
    results.append("="*60)
    results.append(" RÉSULTATS DU TEST DE TRADUCTION COMPLÈTE (EN -> AR)")
    results.append("="*60 + "\n")

    for p in prompts_to_test:
        print(f"Traduction du texte complet avec {p} ({labels[p]})...")
        results.append(f"=== PROMPT {p} ({labels[p]}) ===")
        try:
            # Traduction du texte entier
            trans = translator.translate_text(full_text, "English", "Arabic", mode=p)
            results.append(trans + "\n")
        except Exception as e:
            results.append(f"ERREUR: {e}\n")
        
        results.append("-" * 40 + "\n")
        # Pause plus longue pour un gros bloc
        time.sleep(2)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print(f"\nTerminé ! Le texte complet a été traduit. Résultats dans : {output_file}")

if __name__ == "__main__":
    run_test()
