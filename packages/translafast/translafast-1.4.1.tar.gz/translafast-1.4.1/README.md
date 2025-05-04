# 🌐 TranslaFast v1.4.1

TranslaFast is a blazing-fast, Python-based translation library supporting 178+ languages. It's designed for seamless integration in GUI applications, games, automation tools, and command-line utilities.

---

## 🚀 Features

- 🌐 178 language support  
- 🔁 In-memory caching with optional persistence  
- 🧠 Language name ↔ code conversion (`German` ↔ `de`)  
- 🌍 Automatic language detection  
- 🧩 Batch translation  
- 🧵 Async support  
- 🛡️ Fallback & error handling  
- 📁 File translation  
- 🧪 Testing functions  
- 🌐 REST API (Flask)  
- 🖥️ GUI interface (Tkinter)  
- 💾 Cache export & usage logging  
- 💻 Website language can be changed

---

## 📦 Installation

```bash
pip install translafast
```

---

## 🧪 A Simple Example

```python
# save this as app.py
from translafast import translate
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return translate("Hello, world!", to="tr")  # → "Merhaba dünya!"

@app.route("/api", methods=["POST"])
def api():
    data = request.get_json()
    return jsonify({
        "result": translate(data["text"], to=data.get("to", "en"))
    })

if __name__ == "__main__":
    app.run(debug=True)
```

```bash
$ python app.py
# Running on http://127.0.0.1:5000/
```

---

## 💡 Want More?

```python
from translafast import smart_translate, run_gui

print(smart_translate("Hola"))  # Auto-detects and translates to default language
run_gui()  # Launches the built-in desktop translator
```

---

## 📘 License

MIT © 2025 PozStudio – Free to use with attribution.