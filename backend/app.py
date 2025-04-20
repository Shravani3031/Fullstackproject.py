from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

client = MongoClient("mongodb+srv://shravani:shravani@cluster0.pkfjesd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["mydatabase"]
collection = db["items"]

# GET all items
@app.route("/items", methods=["GET"])
def get_items():
    items = []
    for item in collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return jsonify(items)

# POST a new item
@app.route("/items", methods=["POST"])
def create_item():
    data = request.json
    result = collection.insert_one(data)
    new_item = collection.find_one({"_id": result.inserted_id})
    new_item["_id"] = str(new_item["_id"])
    return jsonify(new_item), 201

# DELETE an item by ID
@app.route("/items/<id>", methods=["DELETE"])
def delete_item(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
