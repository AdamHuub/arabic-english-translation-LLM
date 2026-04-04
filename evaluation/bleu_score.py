import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
import pandas as pd

# Initialisation des ressources NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TranslationEvaluator:
    """
    Classe pour évaluer la qualité des traductions en utilisant le score BLEU.
    Adaptée pour les textes scientifiques Arabe <-> Anglais.
    """
    
    def __init__(self):
        self.smoothing = SmoothingFunction().method1

    def _tokenize(self, text):
        """Tokenisation simple et mise en minuscule."""
        if not text or not isinstance(text, str):
            return []
        return word_tokenize(text.lower())

    def evaluate_sentence(self, reference, candidate):
        """
        Calcule le score BLEU pour une seule phrase.
        """
        ref_tokens = [self._tokenize(reference)]
        cand_tokens = self._tokenize(candidate)
        
        # Calcul du score (pondération par défaut : 1-gram à 4-gram égaux)
        score = sentence_bleu(ref_tokens, cand_tokens, smoothing_function=self.smoothing)
        return score

    def evaluate_corpus(self, list_references, list_candidates):
        """
        Calcule le score BLEU global pour un corpus (ensemble de phrases).
        C'est la métrique standard dans les publications scientifiques.
        """
        # Préparation des données au format NLTK : list de list de list pour refs, list de list pour candidats
        refs_tokenized = [[self._tokenize(ref)] for ref in list_references]
        cands_tokenized = [self._tokenize(cand) for cand in list_candidates]
        
        score = corpus_bleu(refs_tokenized, cands_tokenized, smoothing_function=self.smoothing)
        return score

    def evaluate_dataframe(self, df, ref_column, cand_column):
        """
        Évalue un DataFrame entier et ajoute une colonne de scores individuels.
        Retourne aussi le score global (Corpus BLEU).
        """
        # Scores individuels par ligne
        df['bleu_score'] = df.apply(
            lambda row: self.evaluate_sentence(row[ref_column], row[cand_column]), 
            axis=1
        )
        
        # Score global du corpus
        total_score = self.evaluate_corpus(df[ref_column].tolist(), df[cand_column].tolist())
        
        return df, total_score