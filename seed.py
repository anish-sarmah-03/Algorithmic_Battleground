from app import app
from models import db, User, Submission
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        hashed_password= generate_password_hash("password123")
        test_user= User(username="anish_sarmah", email="heheboi@gmail.com", password_hash= hashed_password, rating=1398)

        db.session.add(test_user)
        db.session.commit()

        mock_data = [
            {"name": "Two Sum", "tag": "Arrays", "diff": "Easy", "status": "AC"},
            {"name": "3Sum", "tag": "Two Pointers", "diff": "Medium", "status": "AC"},
            {"name": "Trapping Rain Water", "tag": "Two Pointers", "diff": "Hard", "status": "WA"},
            {"name": "Coin Change", "tag": "DP", "diff": "Medium", "status": "TLE"},
            {"name": "Climbing Stairs", "tag": "DP", "diff": "Easy", "status": "AC"},
            {"name": "Valid Parentheses", "tag": "Stacks", "diff": "Easy", "status": "AC"},
        ]

        for item in mock_data:
            sub = Submission(
                user_id= test_user.id,
                problem_name= item["name"],
                topic_tag= item["tag"],
                difficulty= item["diff"],
                status = item["status"]
            )
            db.session.add(sub)

        db.session.commit()
        print("Database seeded via test user and test submissions")


if __name__== "__main__":
    seed_database()