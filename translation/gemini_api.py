import google.generativeai as genai
import requests
import json
import logging
import sys
import time
from config import AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL
import translation.prompts as prompts

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("translation_debug.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("UnifiedTranslator")

# Configuration des APIs
if AI_PROVIDER == "gemini":
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info(f"Mode Gemini activé ({GEMINI_MODEL})")
    else:
        logger.error("GEMINI_API_KEY manquante")
elif AI_PROVIDER == "groq":
    if GROQ_API_KEY:
        logger.info(f"Mode Groq activé ({GROQ_MODEL})")
    else:
        logger.error("GROQ_API_KEY manquante")


class TranslatorEngine:
    def __init__(self):
        self.provider = AI_PROVIDER
        print(f"\n[SYSTEM] Moteur de traduction initialisé avec : {self.provider.upper()}\n")

    # ───────────────────── GEMINI ─────────────────────

    def _translate_gemini(self, system_instruction, user_prompt):
        """Non-streaming Gemini call with separated system instruction."""
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                max_output_tokens=4096,
            ),
        )
        response = model.generate_content(user_prompt)
        return response.text

    def _translate_gemini_stream(self, system_instruction, user_prompt):
        """Streaming Gemini call with separated system instruction."""
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                max_output_tokens=4096,
            ),
        )
        response = model.generate_content(user_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    # ───────────────────── GROQ ─────────────────────

    def _translate_groq(self, system_instruction, user_prompt):
        """Non-streaming Groq call with system message."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.8,
            "max_tokens": 4096,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Groq API Error: {response.text}")
            
        result = response.json()
        return result['choices'][0]['message']['content']

    def _translate_groq_stream(self, system_instruction, user_prompt):
        """Streaming Groq call with system message."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.8,
            "max_tokens": 4096,
            "stream": True
        }
        response = requests.post(url, headers=headers, json=data, stream=True)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    content = decoded_line[6:]
                    if content == "[DONE]":
                        break
                    try:
                        json_data = json.loads(content)
                        token = json_data['choices'][0]['delta'].get('content', '')
                        if token:
                            yield token
                    except:
                        continue

    # ───────────────────── DISPATCH ─────────────────────

    def _get_prompt_pair(self, text, source_lang, target_lang, mode):
        """Resolve mode into (system_instruction, user_prompt) tuple."""
        if mode.startswith("V"):
            return prompts.get_global_prompt(mode, text, source_lang, target_lang)
        elif mode == "scientific":
            return prompts.get_scientific_prompt(text, source_lang, target_lang)
        else:
            return prompts.get_creative_prompt(text, source_lang, target_lang)

    def translate_text(self, text, source_lang, target_lang, mode="scientific"):
        if not text or not text.strip():
            return ""

        system_instruction, user_prompt = self._get_prompt_pair(text, source_lang, target_lang, mode)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Traduction via {self.provider} ({mode}) - Tentative {attempt+1}")
                if self.provider == "gemini":
                    raw = self._translate_gemini(system_instruction, user_prompt)
                else:
                    raw = self._translate_groq(system_instruction, user_prompt)

                cleaned = prompts.clean_translation_output(raw, target_lang)
                return cleaned

            except Exception as e:
                err_msg = str(e)
                logger.error(f"Erreur attempt {attempt+1}: {err_msg}")
                
                if "rate_limit" in err_msg.lower() or "429" in err_msg:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Rate limit détecté. Attente de {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(1)
                
                if attempt == max_retries - 1:
                    return f"Erreur : {err_msg}"
        return "Erreur inconnue"

    def translate_text_stream(self, text, source_lang, target_lang, mode="scientific"):
        if not text or not text.strip():
            return ""

        system_instruction, user_prompt = self._get_prompt_pair(text, source_lang, target_lang, mode)

        try:
            logger.info(f"Streaming via {self.provider} ({mode})")

            # Collect full text for post-processing, then yield cleaned result
            full_text = ""
            if self.provider == "gemini":
                for chunk in self._translate_gemini_stream(system_instruction, user_prompt):
                    full_text += chunk
            else:
                for chunk in self._translate_groq_stream(system_instruction, user_prompt):
                    full_text += chunk

            # Post-process the complete text to strip non-target chars
            cleaned = prompts.clean_translation_output(full_text, target_lang)
            logger.info(f"Stream post-processing: {len(full_text)} chars → {len(cleaned)} chars")
            yield cleaned

        except Exception as e:
            logger.error(f"Erreur stream: {e}")
            yield f"Erreur : {str(e)}"


# Singleton pour l'API
_translator = TranslatorEngine()
GeminiTranslator = TranslatorEngine  # Alias pour compatibilité descendante

def translate_text(text, source_lang, target_lang, prompt_type="detailed"):
    if prompt_type.startswith("V"):
        mode = prompt_type
    else:
        mode = "scientific" if prompt_type == "detailed" else "creative"
    return _translator.translate_text(text, source_lang, target_lang, mode)

def translate_text_stream(text, source_lang, target_lang, prompt_type="detailed"):
    if prompt_type.startswith("V"):
        mode = prompt_type
    else:
        mode = "scientific" if prompt_type == "detailed" else "creative"
    return _translator.translate_text_stream(text, source_lang, target_lang, mode)
