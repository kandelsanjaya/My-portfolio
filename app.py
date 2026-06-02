```python
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import json
import os
import re
import requests
from datetime import datetime

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ==========================
# CONFIGURATION
# ==========================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

INQUIRIES_FILE = "inquiries.json"
VISITORS_FILE = "visitors.json"

# ==========================
# CREATE FILES IF MISSING
# ==========================

for file in [INQUIRIES_FILE, VISITORS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

# ==========================
# HELPER FUNCTIONS
# ==========================

def read_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return []

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():

    visitor = {
        "ip": str(hash(request.remote_addr)),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "browser": request.headers.get("User-Agent")
    }

    try:
        visitors = read_json(VISITORS_FILE)
        visitors.append(visitor)
        write_json(VISITORS_FILE, visitors)
    except Exception as e:
        print("Visitor Log Error:", e)

    return render_template("index.html")

# ==========================
# VISITOR API
# ==========================

@app.route("/api/visitors", methods=["GET"])
def get_visitors():

    visitors = read_json(VISITORS_FILE)

    return jsonify({
        "success": True,
        "count": len(visitors)
    })

# ==========================
# CONTACT FORM
# ==========================

@app.route("/contact", methods=["POST"])
def contact():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "message": "Name, Email and Message are required"
        }), 400

    if not validate_email(email):
        return jsonify({
            "success": False,
            "message": "Invalid Email Address"
        }), 400

    inquiry = {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    inquiries = read_json(INQUIRIES_FILE)
    inquiries.append(inquiry)
    write_json(INQUIRIES_FILE, inquiries)

    return jsonify({
        "success": True,
        "message": "Message sent successfully!"
    })

# ==========================
# AI PROMPT GENERATOR
# ==========================

@app.route("/api/generate-prompt", methods=["POST"])
def generate_prompt():

    if not ANTHROPIC_API_KEY:
        return jsonify({
            "success": False,
            "message": "Anthropic API key not configured."
        }), 500

    data = request.get_json()

    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({
            "success": False,
            "message": "Topic is required."
        }), 400

    try:

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-opus-4-1",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content":
                        f"""
                        Create a professional AI prompt about:

                        {topic}

                        Return only the prompt.
                        No markdown.
                        No explanation.
                        """
                    }
                ]
            }
        )

        response.raise_for_status()

        result = response.json()

        generated_prompt = result["content"][0]["text"]

        return jsonify({
            "success": True,
            "prompt": generated_prompt
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ==========================
# DOWNLOAD CV
# ==========================

@app.route("/download-cv")
def download_cv():

    cv_folder = os.path.join(
        app.root_path,
        "static",
        "cv"
    )

    return send_from_directory(
        cv_folder,
        "Sanjaya_Kandel_CV.pdf",
        as_attachment=True
    )

# ==========================
# VIEW CONTACT MESSAGES
# ==========================

@app.route("/api/inquiries")
def inquiries():

    data = read_json(INQUIRIES_FILE)

    return jsonify({
        "success": True,
        "total": len(data),
        "messages": data
    })

# ==========================
# HEALTH CHECK
# ==========================

@app.route("/health")
def health():

    return jsonify({
        "status": "running",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
```
