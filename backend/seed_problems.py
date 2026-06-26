from app import app
from models import db, Problem

def seed_database():
    with app.app_context():
        # Clear existing problems to avoid duplicates if run multiple times
        db.session.query(Problem).delete()
        
        problems = [
            Problem(
                title="Two Sum",
                description="Given an array of integers nums and an integer target, print indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
                difficulty="Easy",
                topic_tag="Arrays",
                test_cases=[
                    {"input": "2 7 11 15\n9\n", "expected_output": "0 1"},
                    {"input": "3 2 4\n6\n", "expected_output": "1 2"},
                    {"input": "3 3\n6\n", "expected_output": "0 1"}
                ]
            ),
            Problem(
                title="Longest Palindromic Substring",
                description="Given a string s, print the longest palindromic substring in s.",
                difficulty="Medium",
                topic_tag="Strings",
                test_cases=[
                    {"input": "babad\n", "expected_output": "bab"},
                    {"input": "cbbd\n", "expected_output": "bb"}
                ]
            ),
            Problem(
                title="Regular Expression Matching",
                description="Given an input string s and a pattern p, implement regular expression matching with support for '.' and '*' where '.' Matches any single character and '*' Matches zero or more of the preceding element. Print 'true' or 'false' indicating whether the matching covers the entire input string.",
                difficulty="Hard",
                topic_tag="Dynamic Programming",
                test_cases=[
                    {"input": "aa\na\n", "expected_output": "false"},
                    {"input": "aa\na*\n", "expected_output": "true"},
                    {"input": "ab\n.*\n", "expected_output": "true"}
                ]
            ),
            Problem(
                title="Pow(x, n)",
                description="Implement pow(x, n), which calculates x raised to the power n. Print the output to 5 decimal places.",
                difficulty="Medium",
                topic_tag="Math",
                test_cases=[
                    {"input": "2.00000\n10\n", "expected_output": "1024.00000"},
                    {"input": "2.10000\n3\n", "expected_output": "9.26100"},
                    {"input": "2.00000\n-2\n", "expected_output": "0.25000"}
                ]
            )
        ]
        
        db.session.add_all(problems)
        db.session.commit()
        print("Successfully seeded 4 LeetCode problems into the database!")

if __name__ == "__main__":
    seed_database()