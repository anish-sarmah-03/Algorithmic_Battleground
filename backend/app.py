from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_socketio import emit, join_room

from models import db, User, CodingRoom, Problem, Match
import os
import random
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from auth import auth_bp
from dashboard import dashboard_bp
from analytics import analytics_bp
from room import room_bp

load_dotenv()

app=Flask(__name__)
migrate = Migrate(app,db)
CORS(app)
socketio= SocketIO(app, cors_allowed_origins="*")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')

db.init_app(app)
jwt=JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(room_bp, url_prefix='/api/room')

with app.app_context():
    db.create_all()
    print("PostgreSql Table created successfully")

@app.route('/')
def home():
    return { "message": "Algorithmic battleground API is running on postgresql"}


@socketio.on('join_arena')
def handle_join_arena(data):
    try:
        room_code = data.get('room_code')
        user_id = data.get('user_id')
        timer_setting = int(data.get('timer_setting', 30))
        
        join_room(room_code)
        
        match = Match.query.filter_by(room_code=room_code).first()
        
        if not match:
            # Player 1 is creating the room
            match = Match(
                room_code=room_code,
                player_1_id=user_id,
                timer_setting=timer_setting,
                status='waiting'
            )
            db.session.add(match)
            db.session.commit()
            
            emit('room_status', {
                'status': 'waiting',
                'message': f'Waiting for an opponent to join...',
                'timer_setting': timer_setting
            }, room=room_code)
            
        elif match.player_1_id != user_id and not match.player_2_id:
            # Player 2 is joining
            match.player_2_id = user_id
            match.status = 'active'
            db.session.commit()
            
            easy_probs = Problem.query.filter_by(difficulty='Easy').all()
            med_probs = Problem.query.filter_by(difficulty='Medium').all()
            hard_probs = Problem.query.filter_by(difficulty='Hard').all()
            
            selected_problems = []
            if easy_probs: selected_problems.append(random.choice(easy_probs))
            if med_probs: selected_problems.append(random.choice(med_probs))
            if hard_probs: selected_problems.append(random.choice(hard_probs))
            
            problems_data = [{'id': p.id, 'title': p.title, 'description': p.description, 'difficulty': p.difficulty, 'topic_tag': p.topic_tag} for p in selected_problems]
            
            emit('match_start', {
                'status': 'active',
                'problems': problems_data,
                'duration_minutes': match.timer_setting
            }, room=room_code)
            
    except Exception as e:
        db.session.rollback() 
        print(f"🚨 SOCKET ERROR: {str(e)}") 

if __name__=='__main__':
    app.run(debug=True)
