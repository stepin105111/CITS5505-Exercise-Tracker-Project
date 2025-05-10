from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from app.database import db, User, WeeklyPlan, WorkoutLog
from datetime import datetime
from flask.cli import with_appcontext
from flask_migrate import Migrate
import click
from datetime import timedelta
from collections import Counter
from collections import defaultdict


app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 604800 # 7 days


db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    if current_user.is_authenticated:
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.update_last_login()
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
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
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
@login_required
def dashboard():
    user = current_user

    weekly_plans = WeeklyPlan.query.filter_by(user_id=user.id).all()

    for plan in weekly_plans:
        plan.start_date = plan.created_at.date()
        plan.end_date = (plan.created_at + timedelta(days=7)).date()

    workout_logs = WorkoutLog.query.filter_by(user_id=user.id).all()

    total_duration = sum([log.duration_minutes for log in workout_logs])
    total_calories = sum([log.calories for log in workout_logs if log.calories])

    workout_days_set = set()
    for log in workout_logs:
        if log.workout_days:
            days = [day.strip() for day in log.workout_days.split(',')]
            workout_days_set.update(days)

    total_workout_days = len(workout_days_set)
    distance_km = 11.5  

    # Visualisation logic -----------------------------------
    
    # 🟦 Pie chart data calculation 
    type_counter = Counter(log.workout_type for log in workout_logs if log.workout_type)
    workout_types = list(type_counter.keys())
    workout_counts = list(type_counter.values())

    # 🟧 Bar chart: Calories per weekday
    from collections import defaultdict
    weekday_calories = defaultdict(int)
    for log in workout_logs:
        if log.workout_days and log.calories:
            for day in log.workout_days.split(','):
                weekday_calories[day.strip()] += log.calories

    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sorted_weekdays = [day for day in weekday_order if day in weekday_calories]
    calories_by_weekday = [weekday_calories[day] for day in sorted_weekdays]

    # 🟪 Line chart: Time spent per weekday (NEW)
    weekday_time_spent = defaultdict(int)
    for log in workout_logs:
        if log.workout_days and log.duration_minutes:
            for day in log.workout_days.split(','):
                weekday_time_spent[day.strip()] += log.duration_minutes

    time_sorted_weekdays = [day for day in weekday_order if day in weekday_time_spent]
    time_by_weekday = [weekday_time_spent[day] for day in time_sorted_weekdays]


    # Progress bar 

    progress_data = {}

    for plan in weekly_plans:
    # Only consider this plan's goal
        goal_calories = plan.calorie_goal
        goal_time = plan.time_goal_minutes

    # Calculate percentage progress from total stats already available
        calorie_ratio = total_calories / goal_calories if goal_calories else 0
        time_ratio = total_duration / goal_time if goal_time else 0

        progress_percent = min((calorie_ratio + time_ratio) / 2 * 100, 100)  # Cap at 100%
        progress_data[plan.plan_name] = round(progress_percent, 1)


    return render_template(
        'dashboard.html',
        user=user,
        weekly_plans=weekly_plans,
        workout_logs=workout_logs,
        total_duration=total_duration,
        total_calories=total_calories,
        total_workout_days=total_workout_days,
        distance_km=distance_km,
        workout_types=workout_types,
        workout_counts=workout_counts,
        weekday_labels=sorted_weekdays,
        weekday_calories=calories_by_weekday,
        time_labels=time_sorted_weekdays,                  
        time_spent_values=time_by_weekday,
        progress_data=progress_data
                                    
    )

@app.route('/create_plan', methods=['POST'])
@login_required
def create_plan():
    
    try:
        new_plan = WeeklyPlan(
            user_id=current_user.id,
            plan_name=request.form.get('plan_name'),
            calorie_goal=int(request.form.get('calorie_goal')),
            time_goal_minutes=int(request.form.get('time_goal_minutes')),
        )
        db.session.add(new_plan)
        db.session.commit()
        flash("Workout plan created successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating plan: {str(e)}", "danger")

    return redirect(url_for('dashboard'))


@app.route('/create_workout', methods=['POST'])
@login_required
def create_workout():
    
    try:
        print("Workout form data:", request.form.to_dict())

        workout = WorkoutLog(
            user_id=current_user.id,
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
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/delete_plan/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):

    plan = WeeklyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    
    if plan:
        try:
            db.session.delete(plan)
            db.session.commit()
            flash("Workout plan deleted successfully.", "info")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting plan: {str(e)}", "danger")
    else:
        flash("Plan not found or unauthorized action.", "warning")

    return redirect(url_for('dashboard'))

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    
    try:
        # Option 1: Delete all logs
        WorkoutLog.query.filter_by(user_id=current_user.id).delete()

        # Option 2 (alternative): Zero out fields instead of deleting
        # logs = WorkoutLog.query.filter_by(user_id=current_user.id).all()
        # for log in logs:
        #     log.duration_minutes = 0
        #     log.calories = 0
        #     log.workout_days = ""
        # db.session.add_all(logs)

        db.session.commit()
        flash("All workout stats have been reset.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error resetting stats: {str(e)}", "danger")

    return redirect(url_for('dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
