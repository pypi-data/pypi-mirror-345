from googletrans import Translator
import json
import os
import asyncio
import atexit

# Dosya yolları
CURRENT_DIR = os.path.dirname(__file__)
LANG_FILE = os.path.join(CURRENT_DIR, "languages.json")
CACHE_FILE = os.path.join(CURRENT_DIR, "cache.json")

# Global translator ve cache
translator = Translator()
translation_cache = {}

# ─────────────────────────────────────────────
# 🔁 ÇEVİRİ FONKSİYONLARI
# ─────────────────────────────────────────────

def translate(text, from_lang="auto", to="en", debug=False, fallback_text=None):
    if not text:
        return ""

    cache_key = f"{from_lang}->{to}:{text.strip().lower()}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    try:
        result = translator.translate(text, src=from_lang, dest=to)
        translation_cache[cache_key] = result.text
        return result.text
    except Exception as e:
        if debug:
            print(f"[TranslaFast Error] {str(e)}")
        return fallback_text if fallback_text is not None else "[Translation Error]"

async def async_translate(text, from_lang="auto", to="en", debug=False, fallback_text=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: translate(text, from_lang, to, debug, fallback_text))

def translate_batch(texts, from_lang="auto", to="en"):
    return [translate(text, from_lang, to) for text in texts]

# ─────────────────────────────────────────────
# 🌍 DİL ALGILAMA VE DÖNÜŞÜM
# ─────────────────────────────────────────────

def detect_language(text):
    try:
        return translator.detect(text).lang
    except Exception:
        return "unknown"

def get_language_name(code):
    langs = get_languages()
    return langs.get(code, code)

def get_language_code(name):
    langs = get_languages()
    for code, lang_name in langs.items():
        if lang_name.lower() == name.lower():
            return code
    return name

def is_valid_language(code):
    return code in get_languages()

def search_language_code(partial_name):
    """
    Girilen kısmî dil adını içeren tüm dil kodlarını döndürür.
    Örn: "chinese" → {'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)'}
    """
    langs = get_languages()
    return {code: name for code, name in langs.items() if partial_name.lower() in name.lower()}

# ─────────────────────────────────────────────
# 📁 DİL VERİ TABANI
# ─────────────────────────────────────────────

def get_languages():
    try:
        with open(LANG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"en": "English", "tr": "Turkish"}

def load_languages(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return get_languages()

def export_languages(filepath="exported_languages.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(get_languages(), f, indent=2, ensure_ascii=False)

def get_supported_language_names():
    return list(get_languages().values())

# ─────────────────────────────────────────────
# 💾 CACHE YÖNETİMİ
# ─────────────────────────────────────────────

def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(translation_cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Cache Save Error] {e}")

def load_cache():
    global translation_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                translation_cache = json.load(f)
    except Exception as e:
        print(f"[Cache Load Error] {e}")

def clear_cache():
    translation_cache.clear()

# Otomatik olarak başlatıldığında cache'i yükle, çıkarken kaydet
load_cache()
atexit.register(save_cache)

# ─────────────────────────────────────────────
# 🧪 TEST
# ─────────────────────────────────────────────

def test_translation():
    print("🧪 Test Başlatıldı")
    print("-> translate: ", translate("Hello", to="tr"))
    print("-> detect: ", detect_language("Bonjour"))
    print("-> code: ", get_language_code("German"))
    print("-> name: ", get_language_name("fr"))
    print("-> valid? ", is_valid_language("de"))
    print("-> batch: ", translate_batch(["hello", "world"], to="es"))
    print("-> search 'chinese': ", search_language_code("chinese"))
