from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

dashboard_bp= Blueprint('dashboard', __name__)
@dashboard_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    curr_user_id = get_jwt_identity()
    user= User.query.get(curr_user_id)
    if not user:
        return jsonify ({"message": "User not found"}), 404
    return jsonify({ 
        "message": "Welcome to you profile",
        "user_id": user.id,
        "username": user.username, 
        "email": user.email, 
        "rating": user.rating
          }), 200


