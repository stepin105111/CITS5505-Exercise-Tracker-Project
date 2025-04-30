from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from app.database import db, User
import os
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

   return render_template(
    'dashboard.html', 
    user=user,
    username=user.username)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/workout-plan')
def workout_plan():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('workout_plan.html')


@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('input.html')

@app.route('/visualise')
def visualise_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('visualise.html')

# Friend search and add functionality
@app.route('/search-users', methods=['GET'])
def search_users():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    query = request.args.get('query', '')
    
    if not query or len(query) < 2:
        return jsonify({'users': []})
    
    # Find users with usernames containing the query
    current_user = User.query.filter_by(username=session['username']).first()
    users = User.query.filter(
        User.username.like(f'%{query}%'), 
        User.id != current_user.id
    ).limit(10).all()
    
    # Format results with friendship status
    results = []
    for user in users:
        results.append({
            'id': user.id,
            'username': user.username,
            'is_friend': current_user.is_friend(user)
        })
    
    return jsonify({'users': results})

@app.route('/add-friend', methods=['POST'])
def add_friend():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    friend_username = request.json.get('username')
    
    if not friend_username:
        return jsonify({'error': 'No username provided'}), 400
    
    current_user = User.query.filter_by(username=session['username']).first()
    friend = User.query.filter_by(username=friend_username).first()
    
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    if current_user.id == friend.id:
        return jsonify({'error': 'Cannot add yourself as a friend'}), 400
    
    if current_user.is_friend(friend):
        return jsonify({'error': 'Already friends with this user'}), 400
    
    try:
        success = current_user.add_friend(friend)
        db.session.commit()
        
        if success:
            return jsonify({'message': f'Added {friend.username} as a friend'})
        else:
            return jsonify({'error': 'Failed to add friend'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error adding friend: {str(e)}'}), 500
    
@app.route('/remove-friend', methods=['POST'])
def remove_friend():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    friend_username = request.json.get('username')
    
    if not friend_username:
        return jsonify({'error': 'No username provided'}), 400
    
    current_user = User.query.filter_by(username=session['username']).first()
    friend = User.query.filter_by(username=friend_username).first()
    
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    if not current_user.is_friend(friend):
        return jsonify({'error': 'Not friends with this user'}), 400
    
    try:
        success = current_user.remove_friend(friend)
        db.session.commit()
        
        if success:
            return jsonify({'message': f'Removed {friend.username} from friends'})
        else:
            return jsonify({'error': 'Failed to remove friend'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error removing friend: {str(e)}'}), 500

@app.route('/friends')
def get_friends():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    current_user = User.query.filter_by(username=session['username']).first()
    friend_list = current_user.get_all_friends()
    
    friends = []
    for friend in friend_list:
        friends.append({
            'id': friend.id,
            'username': friend.username,
            'email': friend.email,
            'last_login': friend.last_login.strftime('%Y-%m-%d %H:%M:%S') if friend.last_login else None
        })
    
    return jsonify({'friends': friends})

@app.route('/share')
def share_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.filter_by(username=session['username']).first()
    friends = current_user.get_all_friends()
    
    # Dummy workout data for each friend (since we don't have real data yet)
    mock_activities = [
        {'type': 'Strength Training', 'calories': 550, 'duration': 60},
        {'type': 'Running', 'calories': 430, 'duration': 45},
        {'type': 'Yoga', 'calories': 280, 'duration': 50},
        {'type': 'Swimming', 'calories': 400, 'duration': 40},
        {'type': 'Cycling', 'calories': 520, 'duration': 55}
    ]
    
    # Assign random activity to each friend
    import random
    from datetime import timedelta
    
    friends_data = []
    for i, friend in enumerate(friends):
        days_ago = i + 1
        activity_index = i % len(mock_activities)
        friends_data.append({
            'username': friend.username,
            'activity': mock_activities[activity_index]['type'],
            'calories': mock_activities[activity_index]['calories'],
            'duration': mock_activities[activity_index]['duration'],
            'shared_days_ago': days_ago
        })

    return render_template('share.html', user=current_user, friends=friends_data)


if __name__ == '__main__':
    app.run(debug=True)