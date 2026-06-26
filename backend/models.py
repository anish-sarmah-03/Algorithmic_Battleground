from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

room_participants = db.Table('room_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('coding_room.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

# The User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Integer, default=1200) 
    
    submissions = db.relationship('Submission', backref='coder', lazy='dynamic')
    rooms_joined = db.relationship('CodingRoom', secondary=room_participants, backref='active_members')

#  The Coding Room Table
class CodingRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="waiting")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#  The Submission Table
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_name = db.Column(db.String(100), nullable=False)
    topic_tag = db.Column(db.String(50), nullable=False) 
    difficulty = db.Column(db.String(10), nullable=False) 
    status = db.Column(db.String(20), nullable=False) 
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Problem(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # 'Easy', 'Medium', 'Hard'
    topic_tag = db.Column(db.String(50), nullable=False)
    test_cases = db.Column(db.JSON, nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    
    player_1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    timer_setting = db.Column(db.Integer, default=30) 
    status = db.Column(db.String(20), default='waiting')
