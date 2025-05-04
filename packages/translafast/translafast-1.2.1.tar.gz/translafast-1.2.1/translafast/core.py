import json
import os
import asyncio
import atexit
import hashlib
import re
import datetime
import requests
from flask import Flask, request, jsonify
from tkinter import Tk, Label, Entry, Button

# ───── DOSYA YOLLARI
CURRENT_DIR = os.path.dirname(__file__)
LANG_FILE = os.path.join(CURRENT_DIR, "languages.json")
CACHE_FILE = os.path.join(CURRENT_DIR, "cache.json")
LOG_FILE = os.path.join(CURRENT_DIR, "translation_log.txt")
CONFIG_FILE = os.path.join(CURRENT_DIR, "default_config.json")

# ───── GLOBAL DEĞİŞKENLER
translation_cache = {}
usage_stats = {"total": 0, "cached": 0, "missed": 0}
config = {"default_to": "en", "daily_limit": 9999}

# ───── CONFIG
def load_default_config():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

load_default_config()

# ───── CACHE ANAHTARI
def generate_cache_key(text, from_lang, to_lang):
    raw = f"{from_lang}->{to_lang}:{text.strip().lower()}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

# ───── TEMEL ÇEVİRİ (Harici motor gizli tutulur)
def _external_translate(text, src, dest):
    try:
        from googletrans import Translator
        translator = Translator()
        return translator.translate(text, src=src, dest=dest).text
    except:
        return "[Translation Failed]"

# ───── STANDART ÇEVİRİ
def translate(text, from_lang="auto", to="en", debug=False, fallback_text=None):
    if not text:
        return ""
    if rate_limit_exceeded():
        return "[Rate Limit Exceeded]"

    key = generate_cache_key(text, from_lang, to)
    usage_stats["total"] += 1

    if key in translation_cache:
        usage_stats["cached"] += 1
        return translation_cache[key]

    try:
        result = _external_translate(text, src=from_lang, dest=to)
        translation_cache[key] = result
        log_translation(text, result, from_lang, to)
        usage_stats["missed"] += 1
        return result
    except Exception as e:
        if debug:
            print(f"[Error] {e}")
        return fallback_text or "[Translation Error]"

# ───── BATCH
def translate_batch(texts, from_lang="auto", to="en"):
    return [translate(t, from_lang, to) for t in texts]

# ───── HTML ÇEVİRİ
def translate_html(html_text, from_lang="auto", to="en"):
    tags = re.findall(r"<[^>]+>", html_text)
    clean_text = re.sub(r"<[^>]+>", "", html_text)
    translated = translate(clean_text, from_lang, to)
    for tag in tags:
        translated = translated.replace(clean_text[:len(tag)], tag + clean_text[:len(tag)], 1)
    return translated

# ───── ALTERNATİF MOTOR
def libre_translate(text, from_lang="auto", to="en"):
    try:
        response = requests.post("https://libretranslate.com/translate", json={
            "q": text, "source": from_lang, "target": to, "format": "text"
        }, timeout=10)
        return response.json()["translatedText"]
    except:
        return "[Backup Translation Error]"

# ───── AKILLI ÇEVİRİ
def smart_translate(text, to=None):
    detected = detect_language(text)
    return translate(text, from_lang=detected, to=to or config["default_to"])

# ───── DİL ALGILAMA
def detect_language(text):
    try:
        from googletrans import Translator
        return Translator().detect(text).lang
    except:
        return "unknown"

# ───── DİL VERİLERİ
def get_languages():
    try:
        with open(LANG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"en": "English", "tr": "Turkish"}

def get_language_name(code): return get_languages().get(code, code)
def get_language_code(name): return next((c for c, n in get_languages().items() if n.lower() == name.lower()), name)
def is_valid_language(code): return code in get_languages()
def search_language_code(part): return {c: n for c, n in get_languages().items() if part.lower() in n.lower()}
def get_supported_language_names(): return list(get_languages().values())

# ───── LOG, CACHE, CONFIG
def log_translation(original, translated, src, tgt):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} | {src}->{tgt} | {original} => {translated}\n")

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, indent=2, ensure_ascii=False)

def load_cache():
    global translation_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                translation_cache = data

def clear_cache(): translation_cache.clear()
def get_cache_history(): return translation_cache
def get_usage_stats(): return usage_stats
def export_cache_json(path="exported_cache.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, indent=2, ensure_ascii=False)
def rate_limit_exceeded(): return usage_stats["total"] >= config.get("daily_limit", 9999)

# ───── GUI
def run_gui():
    def on_translate():
        text = entry.get()
        result = translate(text, to=config["default_to"])
        label_result.config(text=result)

    win = Tk()
    win.title("TranslaFast")
    Label(win, text="Metin Girin:").pack()
    entry = Entry(win, width=50)
    entry.pack()
    Button(win, text="Çevir", command=on_translate).pack()
    label_result = Label(win, text="", wraplength=400)
    label_result.pack()
    win.mainloop()

# ───── API
app = Flask(__name__)

@app.route("/translate", methods=["POST"])
def api_translate():
    data = request.get_json()
    text = data.get("text", "")
    return jsonify({
        "result": translate(text, from_lang=data.get("from", "auto"), to=data.get("to", "en"))
    })

@app.route("/detect", methods=["POST"])
def api_detect():
    data = request.get_json()
    return jsonify({"lang": detect_language(data.get("text", ""))})

def run_api():
    app.run(port=5000)

# ───── TEST
def run_all_tests():
    return {
        "smart": smart_translate("Bonjour", to="tr"),
        "html": translate_html("<b>Hello</b>", to="tr"),
        "cache": get_cache_history(),
        "detect": detect_language("Hallo"),
        "languages": get_supported_language_names()
    }

# Otomatik başlat
load_cache()
atexit.register(save_cache)