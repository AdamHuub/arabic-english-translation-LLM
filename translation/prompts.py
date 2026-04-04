
# ============================================================
#  prompts.py — Tous les prompts du projet de traduction
#  Arabe <-> Anglais avec Gemini
# ============================================================

def get_prompt(prompt_id: str, text: str, direction: str = "AR→EN") -> str:
    """
    Retourne le prompt formaté selon l'ID choisi.
    """

    src, tgt = ("Arabic", "English") if direction == "AR→EN" else ("English", "Arabic")
    tgt_note = "Modern Standard Arabic (الفصحى)" if direction == "EN→AR" else "English"

    prompts = {

        "basic": f"""Translate the following text from {src} to {tgt}:

{text}""",

        "role": f"""You are a professional translator specialized in {src} and {tgt}.
Translate the following text accurately.
Output only the translation, no explanation.

Text: {text}""",

        "scientific": f"""You are an expert translator for scientific Artificial Intelligence research papers.
The text below is extracted from an academic AI paper.

Translate from {src} to {tgt_note}.
Rules:
- Preserve all technical terms in their standard form.
- Use formal academic language.
- Do not add explanations or notes.
- Output only the translated text.

Text: {text}""",

        "detailed": f"""You are an expert {src}-{tgt} translator.

Instructions:
- Translate faithfully, do not add or remove information.
- Keep proper nouns unchanged.
- For ambiguous terms, choose the most common scientific meaning.
- Use formal {tgt_note}.
- Output ONLY the translation, no preamble, no explanation.

Text to translate ({src} → {tgt}):
{text}""",

        "chain_of_thought": f"""Translate the following {src} text to {tgt} step by step:

Step 1 - Identify the key technical terms in the text.
Step 2 - Note any ambiguous or difficult phrases.
Step 3 - Provide the final translation.

{src} text: {text}

Step 1 - Key terms:
Step 2 - Ambiguities:
Step 3 - Final translation:""",

        "auto_detect": f"""You are a bilingual Arabic-English translator.
Detect the language of the input automatically.
If the input is Arabic → translate to English.
If the input is English → translate to Modern Standard Arabic (الفصحى).
Output only the translation, nothing else.

Input: {text}""",

        "with_confidence": f"""You are a professional {src}-{tgt} translator.
Translate the text below, then evaluate your translation.

Output format (strictly follow this):
Translation: <your translation here>
Confidence: <Low / Medium / High>
Notes: <any difficult term or ambiguity, max 1 sentence>

Text ({src} → {tgt}): {text}""",

        # ── New modes ──────────────────────────────────────────────────
        "standard": f"""You are a professional {src}-{tgt} translator.
Translate the following text naturally and accurately, as if written by a native speaker.
Output only the translation, no explanations.

Text: {text}""",

        "creative": f"""You are a literary translator specializing in creative and expressive {src}-{tgt} translation.
Preserve the tone, style, rhythm, and emotional intent of the original text.
Use vivid, natural {tgt_note}. Output only the translation.

Original ({src}): {text}""",
    }

    # Graceful fallback for unknown prompt IDs
    if prompt_id not in prompts:
        prompt_id = "scientific"

    return prompts[prompt_id]


PROMPT_DESCRIPTIONS = {
    "basic":           "Basique — Zero-shot simple",
    "role":            "Avec rôle — Zero-shot + expert",
    "scientific":      "Scientifique — Domaine IA, termes techniques",
    "detailed":        "Détaillé — Instructions précises + format strict",
    "chain_of_thought":"Chain-of-thought — Raisonnement étape par étape",
    "auto_detect":     "Auto-détect — Détecte la langue automatiquement",
    "with_confidence": "Avec confiance — Traduction + score de confiance",
    "standard":        "Standard — Traduction naturelle quotidienne",
    "creative":        "Créatif — Textes littéraires et expressifs",
}
