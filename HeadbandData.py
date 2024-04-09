
import sqlite3
from flask import Flask, request, jsonify
from eeg.py import data

connection=sqlite3.connect('Headband.db')

cursor = connection.cursor()

command1 = """CREATE TABLE IF NOT EXISTS
Headband(O1 float, O2 float, T3 float, T4 float)"""

cursor.execute(command1)

cursor.execute("INSERT INTO Headband VALUES"(data))

connection.commit()
