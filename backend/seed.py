from pymongo import MongoClient

# Connect to local MongoDB (change if you're using MongoDB Atlas)
client = MongoClient("mongodb+srv://shravani:shravani@cluster0.pkfjesd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["mydatabase"]
collection = db["items"]

# Sample data
sample_items = [
    {"name": "Apple", "description": "Fresh red apple", "price": 1.2},
    {"name": "Banana", "description": "Organic bananas", "price": 0.8},
    {"name": "Orange", "description": "Citrusy and sweet", "price": 1.5},
    {"name": "Milk", "description": "1L of whole milk", "price": 2.3},
]

# Insert data
result = collection.insert_many(sample_items)
print(f"Inserted {len(result.inserted_ids)} items.")
