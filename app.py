from flask import Flask
from models import db
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from auth import auth_bp
from dashboard import dashboard_bp
from analytics import analytics_bp

load_dotenv()

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')

db.init_app(app)
jwt=JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

with app.app_context():
    db.create_all()
    print("PostgreSql Table created successfully")

@app.route('/')
def home():
    return { "message": "Algorithmic battleground API is running on postgresql"}

if __name__=='__main__':
    app.run(debug=True)
