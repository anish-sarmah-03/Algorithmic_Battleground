from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, Submission
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)
@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_user_analytics():
    curr_user_id = get_jwt_identity()
    total_count= db.session.query(
        Submission.topic_tag,
        func.count(Submission.id).label('total')
    ).filter(Submission.user_id== curr_user_id).group_by(Submission.topic_tag).all()

    ac_count= db.session.query(
        Submission.topic_tag,
        func.count(Submission.id).label('ac_total')
    ).filter(Submission.user_id == curr_user_id,
    Submission.status=='AC'). group_by(Submission.topic_tag).all()

    stats={}
    for topic, total in total_count:
        stats[topic]={"name": topic, "total": total, "ac": 0}
    for topic, ac in ac_count:
        if topic in stats:
            stats[topic]["ac"]=ac
    
    chart_data = list(stats.values())
    
    return jsonify({
        "message": " Analytics fetched successfully",
        "chart_data": chart_data
    }), 200
