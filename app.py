from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from dotenv import load_dotenv
import os

# ==============================
# 🔹 Load Environment Variables
# ==============================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

collection = None

# ==============================
# 🔹 MongoDB Connection Section
# ==============================

if not MONGO_URI:
    print("❌ MONGO_URI not found in .env file")
else:
    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        # Force connection test
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
        }), 500

    try:
        data = request.json

        filename = data.get("filename")
        url = data.get("url")

        if not filename:
            return jsonify({
                "duplicate": False,
                "error": "Invalid data"
            }), 400

        # 🔹 Duplicate check by filename
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
    app.run(debug=False)
