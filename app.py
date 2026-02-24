from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==============================
# 🔹 MongoDB Connection Section
# ==============================

try:
    client = MongoClient(
        "mongodb+srv://admin:PoorvajaMegha2023@dataalert.umzneoh.mongodb.net/?retryWrites=true&w=majority",
        serverSelectionTimeoutMS=5000
    )

    # Force actual connection test
    client.server_info()

    print("✅ MongoDB Connected Successfully!")

    db = client["datadup_db"]
    collection = db["files"]

except ConnectionFailure as e:
    print("❌ MongoDB Connection Failed!")
    print(e)
    collection = None


# ==============================
# 🔹 Routes
# ==============================

@app.route("/")
def home():
    return "Backend is running"


@app.route("/check", methods=["POST"])
def check_duplicate():

    if collection is None:
        return jsonify({
            "duplicate": False,
            "error": "Database not connected"
        })

    try:
        data = request.json

        filename = data.get("filename")
        url = data.get("url")

        if not filename:
            return jsonify({
                "duplicate": False,
                "error": "Invalid data"
            }), 400

        # 🔹 Duplicate check ONLY by filename
        existing_file = collection.find_one({
            "filename": filename
        })

        if existing_file:
            print("⚠ Duplicate detected:", filename)
            return jsonify({"duplicate": True})

        # 🔹 Store new file record
        collection.insert_one({
            "filename": filename,
            "url": url,
            "timestamp": datetime.utcnow()
        })

        print("✅ File stored:", filename)
        return jsonify({"duplicate": False})

    except Exception as e:
        print("❌ Error in /check:", e)
        return jsonify({
            "duplicate": False,
            "error": "Server error"
        }), 500


# ==============================
# 🔹 Run Server
# ==============================

if __name__ == "__main__":
    app.run(debug=True)