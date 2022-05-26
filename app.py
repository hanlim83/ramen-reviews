from flask import Flask
import sqlite3

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'