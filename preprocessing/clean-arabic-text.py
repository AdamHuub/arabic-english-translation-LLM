# import section

import pyarabic.araby as araby
import re
import os

def convert_ind_arabic_to_latin(text):
    return text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶٧٨٩', '01234567890123456789'))

         #text from user input 
def Arabic_trans(text):
    """
    Fonction de nettoyage robuste pour le texte arabe.
    """
    if not text:
        return "" # Gestion des cas vides pour éviter les plantages
        
    # Normalisation Alef et Teh : Standardise les différentes formes (ex: آ, أ, إ -> ا)
    text = araby.normalize_alef(text) 
    text = araby.normalize_teh(text)
    
    # Suppression du Tatweel (ex: تــــــــم -> تم) pour unifier le vocabulaire
    text = araby.strip_tatweel(text)
    
    # Conservation du Tashkeel (voyelles) : Important pour le sens des mots (sémantique)
    # text = araby.strip_tashkeel(text) # Commenté pour préserver la précision sémantique
    
    # Nettoyage des répétitions de caractères (souvent dues aux erreurs de saisie)
    text = re.sub(r'([ء-ي])\1+', r'\1', text)
    
    # Filtre strict : ne garde que les caractères arabes, les chiffres et les espaces
    # On remplace par "" au lieu de " " pour ne pas ajouter d'espaces inutiles (suppression de la condition)
    text = re.sub(r'[^\s\u0600-\u06FF0-9]', '', text)
    
    # Conversion des chiffres indiens (٠-٩) en chiffres latins (0-9)
    text = convert_ind_arabic_to_latin(text)
    
    # Tokenisation via araby pour obtenir une liste de mots (tokens)
    tokens = araby.tokenize(text)
   
    return tokens # Retourne la liste des tokens (mots)

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_root, 'data/raw/arabic_texts.txt')
    output_path = os.path.join(project_root, 'data/processed/cleaned_arabic.txt')
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
    else:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Reading: {len(lines)} lines from {input_path}")
        
        cleaned_results = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                tokens = Arabic_trans(line)
                cleaned_results.append(f"{i}- {tokens}")
                print(f"Line {i} done - {len(line.split())} words -> {len(tokens)} tokens")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_results))
        
        print(f"\nSaved cleaned text to {output_path}")

