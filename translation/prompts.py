import re
import unicodedata


def get_system_instruction(source_lang, target_lang):
    """Return a strict system-level instruction that enforces clean output."""
    tgt = target_lang.lower()

    if tgt in ["arabic", "arabe", "ar"]:
        charset_rule = (
            "Your output MUST contain ONLY Arabic script characters "
            "(Unicode range U+0600–U+06FF), Arabic numbers, spaces, and standard punctuation (. , ; : ! ? « »). "
            "NEVER include any English, Latin, or transliterated words. "
            "Every word must be fully translated into Arabic — no exceptions."
        )
    elif tgt in ["english", "anglais", "en"]:
        charset_rule = (
            "Your output MUST contain ONLY English Latin characters "
            "(a-z, A-Z), numbers, spaces, and standard punctuation. "
            "NEVER include any Arabic characters or transliterations."
        )
    else:
        charset_rule = (
            f"Your output MUST contain ONLY {target_lang} characters, "
            "numbers, spaces, and standard punctuation."
        )

    return (
        f"You are a professional {source_lang}-to-{target_lang} translator.\n\n"
        "ABSOLUTE RULES — VIOLATION IS FORBIDDEN:\n"
        f"1. {charset_rule}\n"
        "2. Output ONLY the translation — no explanations, no notes, no alternatives, "
        "no introductions like 'Here is the translation:', no commentary whatsoever.\n"
        "3. Do NOT transliterate foreign terms — translate them into natural equivalents.\n"
        "4. Do NOT include the original text or any part of it in the output.\n"
        "5. The response must be EXACTLY and ONLY the translated text, ready to use as-is."
    )


def get_user_prompt(variant_style, text, source_lang, target_lang):
    """Return the user-facing prompt — contains ONLY the style hint and the text to translate."""
    return f"[STYLE: {variant_style}]\n\nTranslate:\n\n{text}"


def get_scientific_prompt(text, source_lang, target_lang):
    """Return (system_instruction, user_prompt) tuple for scientific mode."""
    system = get_system_instruction(source_lang, target_lang)
    user = get_user_prompt("Scientific — preserve technical accuracy while using proper target-language terminology", text, source_lang, target_lang)
    return system, user


def get_creative_prompt(text, source_lang, target_lang):
    """Return (system_instruction, user_prompt) tuple for creative mode."""
    system = get_system_instruction(source_lang, target_lang)
    user = get_user_prompt("Literary and creative — maintain artistic spirit and natural flow", text, source_lang, target_lang)
    return system, user


def get_global_prompt(variant_name, text, source_lang, target_lang):
    """Return (system_instruction, user_prompt) tuple for selected variants (V5, V7, V9)."""
    
    # Dictionnaire des styles conservés avec nouveaux labels
    styles = {
        "V9": "PROMPT1 — Absolute technical precision, using the most advanced and industry-standard terminology available",
        "V5": "PROMPT2 — Elite literary translation, balancing perfect semantic fidelity with the formal elegance of classical Arabic literature. Mirror the vocabulary of professional book translations.",
        "V7": "PROMPT3 — Standard expressive translation, capturing the natural flow and intent"
    }

    # Fallback sur V5 si le nom n'existe pas
    style_instr = styles.get(variant_name, styles["V5"])
    
    system = get_system_instruction(source_lang, target_lang)
    user = get_user_prompt(style_instr, text, source_lang, target_lang)
    return system, user


# ─────────────────────────────────────────
# POST-PROCESSING: strip non-target chars
# ─────────────────────────────────────────

def clean_translation_output(raw_text, target_lang):
    """
    Post-process the LLM output to remove any residual non-target characters,
    meta-commentary, and formatting artifacts.
    """
    text = raw_text.strip()

    # Remove common LLM preamble patterns
    preamble_patterns = [
        r'^(?:here\s+is\s+the\s+translation[:\s]*)',
        r'^(?:the\s+translation\s+is[:\s]*)',
        r'^(?:translation[:\s]*)',
        r'^(?:الترجمة[:\s]*)',
        r'^(?:إليك\s+الترجمة[:\s]*)',
    ]
    for pat in preamble_patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE).strip()

    # Remove wrapping quotes if the entire text is quoted
    if (text.startswith('"') and text.endswith('"')) or (text.startswith('«') and text.endswith('»')):
        text = text[1:-1].strip()

    tgt = target_lang.lower()
    if tgt in ["arabic", "arabe", "ar"]:
        text = _strip_non_arabic(text)
    elif tgt in ["english", "anglais", "en"]:
        text = _strip_non_english(text)

    return text.strip()


def _strip_non_arabic(text):
    """Keep only Arabic characters, numbers, spaces, and punctuation."""
    cleaned_chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        # Arabic Unicode block: U+0600–U+06FF, U+0750–U+077F, U+FB50–U+FDFF, U+FE70–U+FEFF
        cp = ord(ch)
        is_arabic = (0x0600 <= cp <= 0x06FF or
                     0x0750 <= cp <= 0x077F or
                     0xFB50 <= cp <= 0xFDFF or
                     0xFE70 <= cp <= 0xFEFF)
        is_digit = cat.startswith('N')
        is_space = ch in ' \t\n\r'
        is_punct = cat.startswith('P') or ch in '.,;:!?؟،؛«»()[]{}–—-'
        if is_arabic or is_digit or is_space or is_punct:
            cleaned_chars.append(ch)
        # Skip Latin / other script chars entirely
    return ''.join(cleaned_chars)


def _strip_non_english(text):
    """Keep only ASCII Latin characters, numbers, spaces, and punctuation."""
    cleaned_chars = []
    for ch in text:
        cp = ord(ch)
        is_latin = (0x0041 <= cp <= 0x005A or 0x0061 <= cp <= 0x007A)  # A-Z, a-z
        is_digit = ch.isdigit()
        is_space = ch in ' \t\n\r'
        is_punct = ch in '.,;:!?\'"()[]{}–—-/@#$%&*+=<>~`^|\\'
        if is_latin or is_digit or is_space or is_punct:
            cleaned_chars.append(ch)
    return ''.join(cleaned_chars)