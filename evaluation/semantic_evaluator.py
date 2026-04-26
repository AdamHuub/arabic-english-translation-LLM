import os
import sys
import torch
from bert_score import score as bert_score_fn
import sacrebleu
import pandas as pd

class SemanticEvaluator:
    """
    Evaluator class for Semantic similarity using BERTScore and Statistical metrics (BLEU).
    Designed for multilingual support (Arabic, French, English).
    """

    def __init__(self, model_type=None, device=None):
        """
        Initializes the evaluator.
        :param model_type: BERT model to use (default: bert-base-multilingual-cased for multilingual).
        :param device: 'cuda' or 'cpu' (auto-detected if None).
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_type = model_type or "bert-base-multilingual-cased"
        print(f"[INFO] Evaluator initialized on {self.device} using {self.model_type}")

    def evaluate_batch(self, candidates, references, lang="en"):
        """
        Compute BLEU and BERTScore for a batch of translations.
        :param candidates: List of predicted strings.
        :param references: List of reference strings.
        :param lang: Language code (ar, fr, en).
        :return: Dictionary with average scores and details.
        """
        if not candidates or not references or len(candidates) != len(references):
            raise ValueError("Candidates and references must be non-empty and have the same length.")

        # --- 1. Statistical Score: BLEU ---
        # sacrebleu expects a list of lists for references
        bleu = sacrebleu.corpus_bleu(candidates, [references])
        bleu_score = bleu.score

        # --- 2. Semantic Score: BERTScore ---
        # lang is crucial for selecting the right model/preprocessing
        P, R, F1 = bert_score_fn(
            candidates, 
            references, 
            lang=lang, 
            model_type=self.model_type, 
            device=self.device,
            verbose=False
        )

        avg_precision = P.mean().item()
        avg_recall = R.mean().item()
        avg_f1 = F1.mean().item()

        return {
            "bleu": bleu_score,
            "bert_precision": avg_precision,
            "bert_recall": avg_recall,
            "bert_f1": avg_f1,
            "individual_f1": F1.tolist()
        }

    def format_results(self, results, title="Evaluation Results"):
        """Prints a clearly formatted table of results."""
        print("\n" + "="*50)
        print(f"{title:^50}")
        print("="*50)
        print(f"{'Metric':<20} | {'Value':<10}")
        print("-" * 50)
        print(f"{'BLEU Score':<20} | {results['bleu']:.4f}")
        print(f"{'BERT Precision':<20} | {results['bert_precision']:.4f}")
        print(f"{'BERT Recall':<20} | {results['bert_recall']:.4f}")
        print(f"{'BERT F1':<20} | {results['bert_f1']:.4f}")
        print("="*50 + "\n")

if __name__ == "__main__":
    # Example usage / Test
    evaluator = SemanticEvaluator()
    
    # Test cases: Synonyms comparison (where BLEU fails but BERTScore excels)
    refs = [
        "The quick brown fox jumps over the lazy dog",
        "ذهب الولد إلى المدرسة مبكرا"
    ]
    cands = [
        "A fast brown fox leaps over a sleepy dog", # High semantic similarity, low BLEU
        "توجه الطفل إلى المدرسة في وقت مبكر" # Arabic synonyms
    ]
    
    print("Running test evaluation...")
    try:
        # Multilingual test
        res_en = evaluator.evaluate_batch([cands[0]], [refs[0]], lang="en")
        evaluator.format_results(res_en, "Test English (Synonyms)")
        
        res_ar = evaluator.evaluate_batch([cands[1]], [refs[1]], lang="ar")
        evaluator.format_results(res_ar, "Test Arabic (Synonyms)")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure bert-score and torch are installed.")
