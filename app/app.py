from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.database import db, User
import os
from datetime import datetime
from flask.cli import with_appcontext
import click

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 604800 # 7 days

db.init_app(app)

# Command to initialize the database
@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("✅ Database initialized.")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first() if email else None

        if existing_user:
            return render_template('register.html', error='Username already exists')
        if existing_email:
            return render_template('register.html', error='Email already registered')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long')

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=f'Error creating account: {str(e)}')

    return render_template('register.html', error=None)

@app.route('/login',methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['username'] = username
            session['user_id'] = user.id
            user.update_last_login()
            if remember:
                session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', error=None)


@app.route('/dashboard')
def dashboard():
   if 'username' not in session:
        return redirect(url_for('login'))

   user = User.query.filter_by(username=session['username']).first()
   if not user:
        session.clear()
        return redirect(url_for('login'))

   return render_template(
    'dashboard.html', 
    user=user,
    username=user.username)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
