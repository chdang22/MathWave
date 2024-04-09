import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent)

from flask import request, g
from flask_json import json_response
from tools.token_tools import create_token
from tools.logging import logger

from werkzeug.security import generate_password_hash, check_password_hash

from db_con import get_db_instance

def handle_request():
    logger.debug("Login Handle Request")

    username = request.form['username']
    password = request.form['password']
    
    authenticated = 0
    
    authenticated = check_if_user_exists(username, password)

    if authenticated == 1:
        user = {"sub": username}
        return json_response(token=create_token(user), authenticated=True)
    elif authenticated == 2:
        return json_response(status_=401, message='Invalid password', authenticated=False)
    else:
        return json_response(status_=401, message='Invalid username', authenticated=False)

def check_if_user_exists(username_to_check, password_to_check):
    db, cursor = get_db_instance()

    #Checking to see if username exists
    cursor.execute("Select password from users where username = ?", (username_to_check, ))
    hashed_password_in_db = cursor.fetchall()

    if hashed_password_in_db:#8675309
        #username was correct

        is_password_correct = check_password_hash(hashed_password_in_db[0][0], password_to_check)

        #Checking to see if password matches
        if is_password_correct:
            #password was correct
            return 1
        else:
            #password was incorrect
            return 2
        
    #username was incorrect
    return 0