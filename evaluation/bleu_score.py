import os
import sys
import re
import time

# Résout le conflit d'initialisation OpenMP (fréquent avec torch/numpy sur Windows)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import sacrebleu
# Tentative d'importation des dépendances sémantiques
try:
    import torch
    from bert_score import score as bert_score_fn
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

import pyarabic.araby as araby

# Ajout du dossier racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SemanticEvaluator:
    """Évaluation sémantique via BERTScore."""
    def __init__(self, model_type="bert-base-multilingual-cased"):
        if HAS_SEMANTIC:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"
        self.model_type = model_type

    def evaluate_batch(self, candidates, references, lang="en"):
        if not candidates or not references or not HAS_SEMANTIC: 
            return {"bert_f1": 0.0}
        P, R, F1 = bert_score_fn(
            candidates, references, 
            lang=lang, 
            model_type=self.model_type, 
            device=self.device,
            verbose=False
        )
        return {"bert_f1": F1.mean().item()}

class TranslationEvaluator:
    def __init__(self):
        self.sem_eval = SemanticEvaluator()

    def evaluate_specific_prompts(self, source_file, ref_file, src_lang="English", tgt_lang="Arabic"):
        from translation.gemini_api import _translator as translator
        
        print(f"\n>>> AUDIT : {src_lang} -> {tgt_lang}")
        
        if not os.path.exists(source_file) or not os.path.exists(ref_file):
            print("Erreur : Fichiers introuvables.")
            return

        with open(source_file, 'r', encoding='utf-8') as f:
            source_blocks = [t.strip() for t in re.split(r'\n\s*\n', f.read()) if t.strip()]
        with open(ref_file, 'r', encoding='utf-8') as f:
            ref_blocks = [t.strip() for t in re.split(r'\n\s*\n', f.read()) if t.strip()]

        # Évaluation des 3 prompts sélectionnés (V5, V7, V9)
        target_prompts = ["V5", "V7", "V9"]
        results = {}

        for p_v in target_prompts:
            print(f"Traitement PROMPT {p_v[1:]}...", end=" ", flush=True)
            cands, refs = [], []
            for i in range(min(len(source_blocks), len(ref_blocks))):
                try:
                    trans = translator.translate_text(source_blocks[i], src_lang, tgt_lang, mode=p_v)
                    
                    # Détection des erreurs d'API (pour éviter de fausser les scores avec des messages d'erreur)
                    if trans.startswith("Erreur :") or "Rate limit" in trans:
                        continue
                        
                    cands.append(trans)
                    refs.append(ref_blocks[i])
                    time.sleep(0.4)
                except: continue

            if not cands:
                print(f"ÉCHEC (Erreur API sur tous les blocs)")
                results[p_v] = {"bleu": 0.0, "bert": 0.0, "final": 0.0, "error": True}
                continue
            
            # Calcul des scores
            bleu = sacrebleu.corpus_bleu(cands, [refs], tokenize='intl').score
            try:
                bert = self.sem_eval.evaluate_batch(cands, refs, lang=tgt_lang[:2].lower())['bert_f1'] * 100
            except: bert = 0.0
            
            # Calcul de la moyenne
            final = (bleu + bert) / 2 if bert > 0 else bleu
            results[p_v] = {"bleu": bleu, "bert": bert, "final": final, "error": False}
            print("OK")

        # Affichage du score final
        print("\n" + "="*55)
        print(f" AUDIT : {src_lang} -> {tgt_lang}")
        print("="*55)
        for p_v in target_prompts:
            s = results.get(p_v, {"error": True})
            label = "ULTRA MAX" if p_v == "V9" else ("pro" if p_v == "V5" else "standard")
            
            if s.get("error"):
                print(f" PROMPT {p_v[1:]} ({label}) = INDISPONIBLE (Erreur API)")
            else:
                detail = f"BLEU: {s['bleu']:.2f}, BERT: {s['bert']:.2f}" if s['bert'] > 0 else f"BLEU: {s['bleu']:.2f} (BERT N/A)"
                print(f" PROMPT {p_v[1:]} ({label}) = {s['final']:.2f}  [{detail}]")
        print("="*55)

if __name__ == "__main__":
    evaluator = TranslationEvaluator()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    en_raw = os.path.join(root, 'data/raw/english_texts.txt')
    ar_raw = os.path.join(root, 'data/raw/arabic_texts.txt')
    
    # Exécution directe
    evaluator.evaluate_specific_prompts(en_raw, ar_raw, "English", "Arabic")
    evaluator.evaluate_specific_prompts(ar_raw, en_raw, "Arabic", "English")
