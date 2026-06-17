from flask import Flask
from models import db
import os
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    print("PostgreSql Table created successfully")

@app.route('/')
def home():
    return { "message": "Algorithmic battleground API is running on postgresql"}

if __name__=='__main__':
    app.run(debug=True)
