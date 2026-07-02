from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_socketio import emit, join_room
from flask import request
from execution_engine import run_code_in_sandbox

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
        
        # Connect the user's socket to this specific room channel
        join_room(room_code)
        
        # Look up the match in the database
        match = Match.query.filter_by(room_code=room_code).first()
        
        # HELPER: Fetch consistent problems (so if they refresh, they don't get new random ones)
        def get_problems():
            easy = Problem.query.filter_by(difficulty='Easy').first()
            med = Problem.query.filter_by(difficulty='Medium').first()
            hard = Problem.query.filter_by(difficulty='Hard').first()
            probs = [p for p in [easy, med, hard] if p]
            return [{'id': p.id, 'title': p.title, 'description': p.description, 'difficulty': p.difficulty} for p in probs]

        # CASE 1: Room doesn't exist -> Create it
        if not match:
            match = Match(room_code=room_code, player_1_id=user_id, timer_setting=timer_setting, status='waiting')
            db.session.add(match)
            db.session.commit()
            emit('room_status', {'status': 'waiting', 'message': 'Waiting for opponent...', 'timer_setting': timer_setting}, room=room_code)
            
        # CASE 2: Room is waiting for Player 2
        elif match.status == 'waiting':
            if match.player_1_id == user_id:
                # Player 1 refreshed the page. Remind them they are waiting.
                emit('room_status', {'status': 'waiting', 'message': 'Waiting for opponent...', 'timer_setting': match.timer_setting}, to=request.sid)
            else:
                # Player 2 joined! Start the match for EVERYONE in the room.
                match.player_2_id = user_id
                match.status = 'active'
                db.session.commit()
                problems_data = get_problems()
                emit('match_start', {'status': 'active', 'problems': problems_data, 'duration_minutes': match.timer_setting}, room=room_code)
                
        # CASE 3: Room is already Active (Someone refreshed the page or dropped connection)
        elif match.status == 'active':
            if user_id in [match.player_1_id, match.player_2_id]:
                # Send the match data ONLY to the specific user who reconnected to catch them up
                problems_data = get_problems()
                emit('match_start', {'status': 'active', 'problems': problems_data, 'duration_minutes': match.timer_setting}, to=request.sid)
            else:
                # A 3rd random person tried to join a full 1v1 battle
                emit('room_status', {'status': 'error', 'message': 'Match is already full.'}, to=request.sid)

    except Exception as e:
        db.session.rollback() 
        print(f"🚨 SOCKET ERROR: {str(e)}")

@socketio.on('submit_code')
def handle_submit_code(data):
    room_code = data.get('room_code')
    problem_id = data.get('problem_id')
    code = data.get('code')
    language = data.get('language')
    
    problem = Problem.query.get(problem_id)
    if not problem:
        emit('execution_result', {'console_output': 'Error: Problem not found.'}, to=request.sid)
        return

    test_cases = problem.test_cases
    console_output = f"Running {language} code for '{problem.title}'...\n"
    all_passed = True

    for i, tc in enumerate(test_cases):
        expected_input = tc.get('input', '')
        expected_output = tc.get('expected_output', '').strip()

        result = run_code_in_sandbox(language, code, expected_input)

        if result['status'] != 'Accepted':
            all_passed = False
            console_output += f"\n❌ Test Case {i+1}: {result['status']}\n"
            if result.get('compile_output'):
                console_output += f"Compile Output:\n{result['compile_output']}\n"
            if result.get('stderr'):
                console_output += f"Error:\n{result['stderr']}\n"
            break 
            
        actual_output = result.get('stdout', '').strip()
        if actual_output != expected_output:
            all_passed = False
            console_output += f"\n❌ Test Case {i+1}: Wrong Answer\nExpected: {expected_output}\nGot: {actual_output}\n"
            break
        else:
            console_output += f"✅ Test Case {i+1}: Passed\n"

    if all_passed:
        console_output += "\nVERDICT: ACCEPTED 🟢"
    else:
        console_output += "\nVERDICT: FAILED 🔴"

    emit('execution_result', {'console_output': console_output}, to=request.sid)

if __name__=='__main__':
    socketio.run(app, debug=True)
