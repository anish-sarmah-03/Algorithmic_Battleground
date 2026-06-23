import random
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CodingRoom, Submission, User

room_bp = Blueprint('room', __name__)

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k==5))

@room_bp.route('/create', methods=['POST'])
@jwt_required
def create_room():
    curr_user_id = get_jwt_identity()
    user = User.query.get(curr_user_id)

    code= generate_room_code()
    new_room= CodingRoom(room_code = code, created_by = curr_user_id, status='waiting')
    new_room.active_members.append(user) 

    db.session.add(new_room)
    db.session.commit()

    return jsonify({
        "message": "Room created successfully",
        "room_code": code
    }), 201

@room_bp.route('/join', methods=['POST'])
@jwt_required()
def join_room():
    curr_user_id = get_jwt_identity()
    user = User.query.get(curr_user_id)
    data = request.get_json()

    room_code = data.get('room_code')
    room= CodingRoom.query.filter_by(room_code= room_code).first()

    if not room:
        return jsonify({"message": "Room not found"}), 404
    
    if user not in room.active_members:
        room.active_members.append(user)
        db.session.commit()

    return jsonify("message": f"Successfully joined room {room_code}"), 200

@room_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_code():
    curr_user_id = get_jwt_identity()
    data = request.get_json()

    verdicts=["AC", "AC", "WA", "TLE"]  #For trial we r giving AC a 50% weight
    final_verdict= random.choice(verdicts)

    new_submission= Submission(
        user_id= curr_user_id,
        problem_name = data.get('problem_name', 'Unknown Problem'),
        topic_tag= data. get('topic_tag', 'General'),
        difficulty = data.get('difficulty', 'medium'),
        status = final_verdict        
    )

    db.session.add(new_submission)
    db.session.commit()

    return jsonify({"message": "Code execution complete",
                    "verdict": final_verdict
                    }), 200