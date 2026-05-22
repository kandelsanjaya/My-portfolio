from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

INQUIRY_FILE = "inquiries.json"

# Create file if not exists
if not os.path.exists(INQUIRY_FILE):
    with open(INQUIRY_FILE, "w") as f:
        json.dump([], f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/inquiry", methods=["POST"])
def inquiry():
    try:
        data = request.get_json()

        inquiry_data = {
            "name": f"{data.get('firstName')} {data.get('lastName')}",
            "email": data.get("email"),
            "subject": data.get("subject"),
            "message": data.get("message"),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(INQUIRY_FILE, "r") as f:
            inquiries = json.load(f)

        inquiries.append(inquiry_data)

        with open(INQUIRY_FILE, "w") as f:
            json.dump(inquiries, f, indent=4)

        return jsonify({
            "ok": True,
            "message": "Inquiry saved successfully"
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)