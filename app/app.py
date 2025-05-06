from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from app.database import db, User, WeeklyPlan, WorkoutLog
from datetime import datetime
from flask.cli import with_appcontext
from flask_migrate import Migrate
import click

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 604800 # 7 days


db.init_app(app)
migrate = Migrate(app, db)


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
        secret_question = request.form.get('secret_question')
        secret_answer = request.form.get('secret_answer')

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

        # Set secret question and answer if provided
        if secret_question and secret_answer:
            new_user.secret_question = secret_question
            new_user.set_secret_answer(secret_answer)


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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user and user.secret_question:
            question_texts = {
                'first_pet': 'What was the name of your first pet?',
                'birth_city': 'In what city were you born?',
                'mother_maiden': 'What is your mother\'s maiden name?',
                'first_school': 'What was the name of your first school?',
                'favorite_food': 'What is your favorite food?'
            }
            question_text = question_texts.get(user.secret_question, user.secret_question)

            return render_template('forgot_password.html',
                                   step='security_question',
                                   username=username,
                                   security_question=question_text)
        else:
            return render_template('forgot_password.html',
                                   step='username',
                                   error='Username not found or no security question set')
    return render_template('forgot_password.html', step='username')
    

@app.route('/verify-answer', methods=['POST'])
def verify_answer():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    answer = request.form.get('answer')

    user = User.query.filter_by(username=username).first()

    if user and user.check_secret_answer(answer):
        return render_template('forgot_password.html', step='reset_password', username=username)
    else:
        question_texts = {
            'first_pet': 'What was the name of your first pet?',
            'birth_city': 'In what city were you born?',
            'mother_maiden': 'What is your mother\'s maiden name?',
            'first_school': 'What was the name of your first school?',
            'favorite_food': 'What is your favorite food?'
        }
        question_text = question_texts.get(user.secret_question, user.secret_question) if user else ""

        return render_template('forgot_password.html', 
            step='security_question', 
            username=username, 
            security_question=question_text,
            error='Incorrect answer. Please try again.')
    
@app.route('/reset-password', methods=['POST'])
def reset_password():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        return render_template('forgot_password.html', 
            step='reset_password', 
            username=username,
            error='Passwords do not match')
    
    if len(new_password) < 6:
        return render_template('forgot_password.html', 
            step='reset_password', 
            username=username,
            error='Password must be at least 6 characters long')
    
    user = User.query.filter_by(username=username).first()

    if user:
        try:
            user.set_password(new_password)
            db.session.commit()
            flash('Password has been reset. Please login with your new password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('forgot_password.html', 
                step='reset_password', 
                username=username,
                error=f'An error occurred: {str(e)}')
    else:
        return render_template('forgot_password.html', step='username', error='User not found')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    workout_logs = WorkoutLog.query.filter_by(user_id=user.id).all()


    # Calculate stats
    total_duration = sum([log.duration_minutes for log in workout_logs])
    total_calories = sum([log.calories for log in workout_logs if log.calories])
     # Calculate unique workout days
    workout_days_set = set()
    for log in workout_logs:
        if log.workout_days:
            days = [day.strip() for day in log.workout_days.split(',')]
            workout_days_set.update(days)

    total_workout_days = len(workout_days_set)
    
    distance_km = 11.5  

    return render_template(
        'dashboard.html',
        user=user,
        workout_logs=workout_logs,
        total_duration=total_duration,
        total_calories=total_calories,
        total_workout_days=total_workout_days,
        distance_km=distance_km
    )


@app.route('/create_workout', methods=['POST'])
def create_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        print("Workout form data:", request.form.to_dict())

        workout = WorkoutLog(
            user_id=session['user_id'],
            plan_name=request.form.get('plan_name'),
            description=request.form.get('description'),
            duration_minutes=int(request.form.get('duration_minutes')),
            workout_type=request.form.get('workout_type'),
            calories=int(request.form.get('calories') or 0),
            intensity=request.form.get('intensity'),
            workout_days=request.form.get('workout_days'), 
        )
        db.session.add(workout)
        db.session.commit()
        flash("Workout logged successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error logging workout: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
