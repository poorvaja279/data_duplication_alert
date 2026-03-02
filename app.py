from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from dotenv import load_dotenv
import hashlib
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
# 🔹 Helper Function: SHA256 Hash
# ==============================

def generate_hash(file_path):
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)

    return hasher.hexdigest()


# ==============================
# 🔹 Routes
# ==============================

@app.route("/")
def home():
    return "Backend is running"


# ---------------------------------
# 🔹 Basic Metadata Duplicate Check
# ---------------------------------

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

        existing_file = collection.find_one({
            "filename": filename
        })

        if existing_file:
            print("⚠ Duplicate detected (metadata):", filename)
            return jsonify({"duplicate": True})

        collection.insert_one({
            "filename": filename,
            "url": url,
            "timestamp": datetime.utcnow()
        })

        print("✅ File stored (metadata):", filename)
        return jsonify({"duplicate": False})

    except Exception as e:
        print("❌ Error in /check:", e)
        return jsonify({
            "duplicate": False,
            "error": "Server error"
        }), 500


# ---------------------------------
# 🔹 Content-Based Hash Duplicate Check
# ---------------------------------

@app.route("/hash_check", methods=["POST"])
def hash_check():

    if collection is None:
        return jsonify({
            "duplicate": False,
            "error": "Database not connected"
        }), 500

    try:
        data = request.json
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({
                "duplicate": False,
                "error": "File path missing"
            }), 400

        if not os.path.exists(file_path):
            return jsonify({
                "duplicate": False,
                "error": "File does not exist"
            }), 400

        file_hash = generate_hash(file_path)

        existing_file = collection.find_one({
            "hash": file_hash
        })

        if existing_file:
            print("⚠ Duplicate detected (hash):", file_path)
            return jsonify({"duplicate": True})

        collection.insert_one({
            "hash": file_hash,
            "file_path": file_path,
            "timestamp": datetime.utcnow()
        })

        print("✅ File stored (hash):", file_path)
        return jsonify({"duplicate": False})

    except Exception as e:
        print("❌ Error in /hash_check:", e)
        return jsonify({
            "duplicate": False,
            "error": "Server error"
        }), 500


# ==============================
# 🔹 Run Server
# ==============================

if __name__ == "__main__":
    app.run(debug=False)
