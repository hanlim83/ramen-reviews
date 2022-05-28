from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3

app = Flask(__name__,static_url_path='',static_folder='static')
app.config['SECRET_KEY'] = 'Wheatley'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    reviews = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    return render_template('index.html', reviews = reviews)