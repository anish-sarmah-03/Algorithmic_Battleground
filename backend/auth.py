from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp= Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data= request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already registered"}), 409
    
    hashed_password = generate_password_hash(data['password'])
    new_user= User(
        username= data['username'],
        email=data['email'],
        password_hash = hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data= request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message" : "Missing email/password"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token= create_access_token(identity=str(user.id))
        return jsonify(
            {
                "message": "Login successfull",
                "access_token": access_token,
                "username": user.username
            }
        ), 200
    
    return jsonify({"message": "Invalid email or password"}), 401


