from flask import render_template
from app import application


@application.route('/')
def index():
    return render_template('index.html')

@application.route('/register')
def register():
    return render_template('register.html')

@application.route('/login')
def login():
    return render_template('login.html')

@application.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')