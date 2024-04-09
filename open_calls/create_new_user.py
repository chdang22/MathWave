import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent)

from flask import request, g
from flask_json import json_response
from werkzeug.security import generate_password_hash
from tools.logging import logger

from db_con import get_db_instance

def is_username_taken(username, cursor):
    try:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        existing_username = cursor.fetchone()
        return existing_username is None
    except Exception as e:
        print("Error checking username:", e)
        return True

def create_users_table_if_not_exists(cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                date_of_birth DATE,
                grade_level TEXT
            )
        """)
    except Exception as e:
        print("Error creating 'users' table:", e)

def add_user(username, hashed_password, first_name, last_name, date_of_birth, grade_level):
    try:
        db, cursor = get_db_instance()
        create_users_table_if_not_exists(cursor)
        print("trying to create new table")

        if is_username_taken(username, cursor):
            return "Username already taken"

        cursor.execute("INSERT INTO users (username, password, first_name, last_name, date_of_birth, grade_level) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, hashed_password, first_name, last_name, date_of_birth, grade_level))
        db.commit()
        return "User added successfully"
    except Exception as e:
        print("Error adding user:", e)
        return "Error adding user"
    finally:
        db.close()

def handle_request():
    print("got to handle request")
    logger.debug("Handle New User Request")

    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    grade_level = request.form['grade_level']

    hashed_password = generate_password_hash(password)

    

    return json_response(status_=200, message=add_user(username, hashed_password, first_name, last_name, date_of_birth, grade_level))

if __name__ == '__main__':
    db, cursor = get_db_instance()

    print("Displaying what tables have been created")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    all_tables = cursor.fetchall()

    if all_tables:
        for r in all_tables:
            print(r)
    else:
        print("No tables to display.")        
        print("Creating a table called 'users' with fields 'username', 'password', 'first_name', 'last_name', 'date_of_birth', 'grade_level'")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                date_of_birth DATE,
                grade_level TEXT
            )
        """)

    #Creating test entry
    cursor.execute("Select username from users where username = 'johndoe'")
    if not cursor.fetchall():
        cursor.execute("INSERT into users (username, password, first_name, last_name, date_of_birth, grade_level) VALUES ('johndoe', ?, 'John', 'Doe', '01/01/1988', '12')", (generate_password_hash('8675309'), ))
        db.commit()

    #cursor.execute("delete from users where username = 'johndoe'")
    
    db.commit()
    print("Displaying all entries in the 'users' table")
    cursor.execute("SELECT * from users")
    print(cursor.fetchall())
