import os
import sys
import ast
import re
import time

# Ajout du dossier racine au chemin de recherche pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translation.gemini_api import _translator as translator
from evaluation.bleu_score import TranslationEvaluator

def parse_cleaned_file(file_path):
    """
    Parse le fichier des tokens nettoyés.
    Format attendu : "index- [tokens...]"
    """
    references = {}
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable.")
        return references

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Extraction de l'index et de la liste de tokens
            match = re.match(r'(\d+)-\s*(.*)', line)
            if match:
                idx = int(match.group(1))
                tokens_str = match.group(2)
                try:
                    # Conversion de la chaîne représentant la liste en véritable liste Python
                    tokens = ast.literal_eval(tokens_str)
                    # On rejoint les tokens par des espaces pour SacreBLEU
                    references[idx] = " ".join(tokens)
                except Exception as e:
                    print(f"Erreur de parsing à l'index {idx}: {e}")
    
    return references

def run_comparison():
    evaluator = TranslationEvaluator()
    
    # Chemins des fichiers
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    english_file = os.path.join(project_root, 'data/raw/english_texts.txt')
    arabic_ref_file = os.path.join(project_root, 'data/processed/cleaned_arabic.txt')
    
    # Chargement des références (tokens regroupés par index de ligne)
    references = parse_cleaned_file(arabic_ref_file)
    if not references:
        print("Aucune référence trouvée. Arrêt.")
        return

    # Lecture du texte source anglais
    if not os.path.exists(english_file):
        print(f"Erreur : {english_file} introuvable.")
        return
        
    with open(english_file, 'r', encoding='utf-8') as f:
        english_lines = f.readlines()

    # Prompts à tester (V1, V6, V9)
    target_prompts = ["V1", "V6", "V9"]
    prompt_names = {
        "V1": "PROMPT 1 (Minimalist)",
        "V6": "PROMPT 6 (Expressive)",
        "V9": "PROMPT 9 (Modern/Digital)"
    }
    
    prompt_scores = {p: [] for p in target_prompts}

    print("\n" + "="*70)
    print(f"{'AUDIT DE TRADUCTION : COMPARAISON DES 3 MEILLEURS PROMPTS':^70}")
    print("="*70)
    print(f"Source : {english_file}")
    print(f"Référence : {arabic_ref_file}\n")

    # Itération sur les lignes qui ont une référence
    for idx, ref_text in sorted(references.items()):
        # On récupère la ligne correspondante dans le fichier anglais (idx-1 car enumerate commence à 1)
        if idx-1 < len(english_lines):
            source_text = english_lines[idx-1].strip()
            if not source_text:
                continue
                
            print(f"\n--- Paragraphe (Ligne {idx}) ---")
            print(f"Source (EN) : {source_text[:100]}...")
            
            for p_v in target_prompts:
                try:
                    # Traduction via le prompt spécifié
                    translation = translator.translate_text(
                        source_text, 
                        "English", 
                        "Arabic", 
                        mode=p_v
                    )
                    
                    # Calcul du score BLEU par rapport aux tokens de référence
                    score = evaluator.evaluate_sentence(ref_text, translation)
                    prompt_scores[p_v].append(score)
                    
                    print(f"  [{p_v}] BLEU: {score:.4f}")
                    
                    # Petit délai pour éviter les limites d'API
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  [{p_v}] Erreur : {e}")

    # Affichage du résumé final
    print("\n" + "="*70)
    print(f"{'RÉSULTATS FINAUX (MOYENNE BLEU)':^70}")
    print("-"*70)
    
    best_prompt = None
    best_avg = -1
    
    for p_v in target_prompts:
        scores = prompt_scores[p_v]
        avg = sum(scores) / len(scores) if scores else 0
        
        indicator = ""
        if avg > best_avg:
            best_avg = avg
            best_prompt = p_v
            
        print(f"{prompt_names[p_v]:<30} | Score : {avg:.4f}")
        
    print("-"*70)
    print(f"MEILLEUR PROMPT : {prompt_names[best_prompt]} ({best_avg:.4f})")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_comparison()
