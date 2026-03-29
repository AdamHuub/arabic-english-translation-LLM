import nltk, string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
nltk.download('punkt',quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

stemmer = PorterStemmer()

def clean_english(text):
    text   = text.lower()
    text   = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stops  = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stops]
    tokens = [stemmer.stem(w) for w in tokens]
    return tokens

if __name__ == '__main__': 
   
   with open('data/raw/english_texts.txt', 'r', encoding='utf-8') as f:
    content = f.read()

    parts = re.split(r'##TEXT\d+##', content)
    texts = [t.strip() for t in parts if t.strip()]

    print(f"Number of texts found: {len(texts)}\n")
     
    cleaned_results = []

    for i, text in enumerate(texts, 1):
        tokens = clean_english(text)
        cleaned_results.append(f"{i}- {tokens}")
        print(f"Text {i} done — {len(text.split())} words → {len(tokens)} tokens")

    with open('data/processed/cleaned_english.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(cleaned_results))
   