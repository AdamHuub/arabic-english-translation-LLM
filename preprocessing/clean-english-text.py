import nltk, string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import os

# Téléchargement des ressources nécessaires pour NLTK
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialisation du stemmer pour réduire les mots à leur racine (ex: "running" -> "run")
stemmer = PorterStemmer()

def clean_english(text):
    """
    Nettoyage poussé pour le texte anglais : minuscules, ponctuation, stopwords et stemming.
    """
    # Passage en minuscules pour la standardisation
    text = text.lower()
    
    # Suppression de la ponctuation pour ne garder que les mots porteurs de sens
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Découpage de la phrase en mots individuels (tokens)
    tokens = word_tokenize(text)
    
    # Chargement des mots de liaison (stopwords) à ignorer
    stops = set(stopwords.words('english'))
    
    # Filtrage des stopwords : On ne garde que les mots significatifs
    tokens = [w for w in tokens if w not in stops]
    
    # Stemming : Réduction des mots à leur forme racine
    tokens = [stemmer.stem(w) for w in tokens]
    
    return tokens # Retourne la liste des tokens (mots racines)

if __name__ == '__main__': 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_root, 'data/raw/english_texts.txt')
    output_path = os.path.join(project_root, 'data/processed/cleaned_english.txt')
    
    if not os.path.exists(input_path):
        print(f"Erreur : {input_path} introuvable.")
    else:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Découpage du contenu basé sur les balises ##TEXT## (ex: ##TEXT1##)
        parts = re.split(r'##TEXT\d+##', content)
        texts = [t.strip() for t in parts if t.strip()]

        print(f"Nombre de textes trouvés : {len(texts)}\n")
         
        cleaned_results = []

        for i, text in enumerate(texts, 1):
            # Nettoyage de chaque bloc de texte
            tokens = clean_english(text)
            # Formatage du résultat final : index- [liste des tokens]
            cleaned_results.append(f"{i}- {tokens}")
            print(f"Texte {i} traité — {len(text.split())} mots -> {len(tokens)} tokens")

        # Sauvegarde des résultats nettoyés (séparés par deux retours à la ligne)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(cleaned_results))
        
        print(f"\nTexte anglais nettoyé sauvegardé dans : {output_path}")