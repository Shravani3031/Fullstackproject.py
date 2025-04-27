from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
import datetime
from pymongo import MongoClient
from flask_cors import CORS  # Import CORS
from bson import ObjectId  # To handle MongoDB ObjectId

# === CONFIGURATION ===
SECRET_KEY = 'secret'
MONGO_URI = 'mongodb+srv://shravani:shravani@cluster0.pkfjesd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# === INITIALIZE APP ===
app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)  # Enable CORS for all routes

# === DATABASE SETUP ===
client = MongoClient(MONGO_URI)
db = client['insta']  # Define your database name
users_collection = db.users
posts_collection = db.posts
stories_collection = db.stories

# === TOKEN CREATION ===
def create_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# === ROUTES ===

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    users_collection.insert_one({'email': data['email'], 'password': hashed_pw})
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({'email': data['email']})
    if not user or not bcrypt.check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_token(user['_id'])
    return jsonify({'token': token})

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
        return jsonify({'message': f'Authenticated user {user_id}'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

# === NEW FEATURE: CREATE POST ===
@app.route('/post', methods=['POST'])
def create_post():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    post_data = {
        'user_id': ObjectId(user_id),
        'description': data['description'],
        'image_url': data['image_url'],
        'created_at': datetime.datetime.utcnow()
    }
    posts_collection.insert_one(post_data)
    return jsonify({'message': 'Post created successfully'}), 201

# === NEW FEATURE: ADD STORY ===
@app.route('/story', methods=['POST'])
def add_story():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Default expiration is 24 hours from now
    if 'expiration' in data:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=data['expiration'])

    story_data = {
        'user_id': ObjectId(user_id),
        'image_url': data['image_url'],
        'created_at': datetime.datetime.utcnow(),
        'expires_at': expiration_time
    }
    stories_collection.insert_one(story_data)
    return jsonify({'message': 'Story added successfully'}), 201

# === MAIN EXECUTION ===
if __name__ == '__main__':
    app.run(debug=True)
