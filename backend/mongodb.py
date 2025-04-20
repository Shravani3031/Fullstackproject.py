from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB config (Change this URI as needed)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)

# Collection
collection = mongo.db.items


# GET all items
@app.route("/items", methods=["GET"])
def get_items():
    items = []
    for item in collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return jsonify(items)


# GET single item by ID
@app.route("/items/<id>", methods=["GET"])
def get_item(id):
    item = collection.find_one({"_id": ObjectId(id)})
    if item:
        item["_id"] = str(item["_id"])
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404


# POST a new item
@app.route("/items", methods=["POST"])
def create_item():
    data = request.json
    result = collection.insert_one(data)
    new_item = collection.find_one({"_id": result.inserted_id})
    new_item["_id"] = str(new_item["_id"])
    return jsonify(new_item), 201


# PUT (update) an item by ID
@app.route("/items/<id>", methods=["PUT"])
def update_item(id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count:
        updated_item = collection.find_one({"_id": ObjectId(id)})
        updated_item["_id"] = str(updated_item["_id"])
        return jsonify(updated_item)
    return jsonify({"error": "Item not found"}), 404


# DELETE an item by ID
@app.route("/items/<id>", methods=["DELETE"])
def delete_item(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
