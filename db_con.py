# Needed for Postgres
# import psycopg2 

# Use SQLite
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('local_data_base')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/get-calibration', methods=['GET'])
def get_calibration():
    calibration = calculate_calibration()
    return jsonify({'calibration': calibration})

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form['feedback']
    conn = get_db_connection()
    conn.execute('INSERT INTO shared_content (feedback) VALUES (?)', (feedback,))
    conn.commit()

    # Calculate the average feedback
    all_feedback = conn.execute('SELECT feedback FROM shared_content').fetchall()
    average_feedback = sum(f['feedback'] for f in all_feedback) / len(all_feedback)

    conn.close()
    return jsonify({'message': 'Feedback submitted successfully', 'average_feedback': average_feedback})
def calculate_calibration():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT AVG(data_column) FROM users')
    avg = cur.fetchone()[0]
    conn.close()
    return avg if avg is not None else 0
def get_db():
    return sqlite3.connect("local_data_base")

def get_db_instance(): 
    db = get_db()
    cur = db.cursor()
    return db, cur 

def setup_database(db, cur):
    cur.execute("ALTER TABLE users ADD COLUMN calibration REAL;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shared_content (
            id INTEGER PRIMARY KEY,
            entertainment_videos TEXT,
            educational_videos TEXT,
            feedback SMALLINT
        );
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS music (song_name VARCHAR(255), rating INT);")
    db.commit()

def insert_educational_videos(db, cur, urls):
    query = "INSERT INTO shared_content (educational_videos) VALUES (?);"
    for url in urls:
        cur.execute(query, (url,))
    db.commit()

def insert_entertainment_videos(db, cur, urls):
    query = "INSERT INTO shared_content (entertainment_videos) VALUES (?);"
    for url in urls:
        cur.execute(query, (url,))
    db.commit()

if __name__ == "__main__":
    db, cur = get_db_instance()
    setup_database(db, cur)

    educational_video_urls = [
        "https://youtu.be/tVHOBVAFjUw?si=qIrhAFfx_fnOq1uv",
        "https://youtu.be/AaxrqDuw1Xk?si=sdNsotVB0imZFex4",
        "https://youtu.be/Hwr4gEHepOo?si=XpVui6tF0-1K1TWOnow"
    ]
    insert_educational_videos(db, cur, educational_video_urls)

    entertainment_video_urls = [
        "https://youtu.be/3y9-dqtqlZE?si=KssdN55Zq2Qnd6GI",
        "https://youtu.be/YLslsZuEaNE?si=d3DvF5X5s9kpxMwJ",
        "https://youtu.be/1iSGc7SX-RU?si=8Fv-B2rOrsKC2CyZ"
    ]
    insert_entertainment_videos(db, cur, entertainment_video_urls)

    cur.execute("SELECT * FROM users;")
    for r in cur.fetchall():
        print(r)

    db.close()

    # Start the Flask app
    app.run(debug=True)
 
