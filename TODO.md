# TODO: Refonte de la Logique de Nettoyage et Évaluation BLEU

Ce document répertorie les tâches nécessaires pour harmoniser le nettoyage des textes et améliorer la précision du calcul du score BLEU dans le projet de traduction Arabe-Anglais.

## 1. Amélioration du Nettoyage des Textes (Text Cleaning)
- [x] **Unification du Nettoyage**: Créer une fonction de nettoyage commune utilisée à la fois pour le prétraitement des données et pour l'évaluation.
- [x] **Normalisation Arabe Avancée**:
    - [x] Utiliser `pyarabic.araby` pour normaliser systématiquement les Alefs, Tehs, et supprimer les Tatweels.
    - [x] Gérer les voyelles (Harakaat) de manière cohérente (les supprimer pour l'évaluation).
- [x] **Normalisation Anglaise**:
    - [x] Mise en minuscule systématique.
    - [x] Suppression des espaces superflus et normalisation de la ponctuation.
- [x] **Nettoyage Post-Traduction**: Renforcer `clean_translation_output` dans `prompts.py` pour éliminer tout résidu de texte non cible.

## 2. Refonte du Calcul du Score BLEU
- [x] **Migration vers SacreBLEU**:
    - [x] Remplacer `nltk.translate.bleu_score` par `sacrebleu` pour des résultats conformes aux standards de la recherche scientifique.
    - [x] Utiliser `sacrebleu.sentence_bleu` et `sacrebleu.corpus_bleu`.
- [x] **Prétraitement avant BLEU**:
    - [x] Implémenter une méthode `clean_text` dans `TranslationEvaluator` qui nettoie la référence et le candidat de la même manière avant le calcul.
    - [x] Option pour ignorer la ponctuation et la casse lors de l'évaluation.
- [x] **Support Multi-Ngram**: S'assurer que le score prend bien en compte les n-grammes de 1 à 4 avec les poids standards.

## 3. Mise à jour des Scripts d'Évaluation
- [ ] **Mise à jour de `run_eval.py`**:
    - [ ] Adapter l'appel à `TranslationEvaluator` pour refléter les changements d'API.
    - [ ] Ajouter des métriques supplémentaires si nécessaire (ex: CHRF).
- [ ] **Validation des Résultats**: Relancer l'audit global avec la nouvelle logique pour confirmer la validité des scores obtenus par les différentes variantes de prompts.

## 4. Documentation et Rapport
- [ ] Documenter la nouvelle logique de calcul dans le rapport final (planning.txt / memoire.tex).
- [ ] Expliquer pourquoi SacreBLEU a été choisi par rapport à NLTK (reproductibilité, tokenisation interne standardisée).
