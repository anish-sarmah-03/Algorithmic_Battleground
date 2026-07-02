from app import app, db
from models import Problem

def seed_passing_chain():
    with app.app_context():
        # Clear old problems to focus only on this one
        Problem.query.delete()
        
        description_html = """
        <p><strong>N</strong> football players stand in a line in order to practice their passes.</p>
        <p>The players are numbered 1 to <strong>N</strong>. Initially, player 1 has the ball.</p>
        <p>All the players have a passing power of <strong>K</strong>. At any point of time, if player <strong>X</strong> has the ball:</p>
        <ul>
            <li>If <strong>X + K &le; N</strong>, the ball will be passed to player <strong>X + K</strong>.</li>
            <li>Otherwise, the ball will remain with player <strong>X</strong>.</li>
        </ul>
        <p>You are given <strong>N</strong> and <strong>K</strong>. Find the number of the player who will have the ball in the end, given that player 1 starts with it.</p>
        
        <br/>
        <h3>Input Format</h3>
        <ul>
            <li>The first line of input will contain a single integer <strong>T</strong>, denoting the number of test cases.</li>
            <li>Each test case consists of a single line of input, containing two space-separated integers <strong>N</strong> and <strong>K</strong>.</li>
        </ul>

        <br/>
        <h3>Output Format</h3>
        <p>For each test case, output on a new line the answer: the number of the player who will have the ball in the end.</p>

        <br/>
        <h3>Constraints</h3>
        <ul>
            <li>1 &le; T &le; 2500</li>
            <li>1 &le; N, K &le; 50</li>
        </ul>
        
        <br/>
        <h3>Sample 1</h3>
        <pre style="background:#1e1e1e; padding:10px; border-radius:5px;">
Input:
4
4 1
6 2
6 7
11 6

Output:
4
5
1
7
        </pre>
        """

        passing_chain = Problem(
            title="Passing Chain",
            description=description_html,
            difficulty="Easy",
            topic_tag="Math",
            test_cases=[
                {
                    "input": "4\n4 1\n6 2\n6 7\n11 6\n",
                    "expected_output": "4\n5\n1\n7"
                }
            ]
        )
        
        db.session.add(passing_chain)
        db.session.commit()
        print("Successfully seeded 'Passing Chain' into the database!")

if __name__ == '__main__':
    seed_passing_chain()