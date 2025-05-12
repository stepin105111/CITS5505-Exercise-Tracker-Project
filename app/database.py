from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from datetime import datetime

# Initialize the database
db = SQLAlchemy()


# Friendship association table
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    secret_question = db.Column(db.String(100), nullable=True)
    secret_answer_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Define the many-to-many relationship for friends
    friends = db.relationship(
        'User',
        secondary=friendships,
        primaryjoin=(friendships.c.user_id == id),
        secondaryjoin=(friendships.c.friend_id == id),
        backref=db.backref('friended_by', lazy='dynamic'),
        lazy='dynamic'
    )
    
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set the password hash from the provided password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_secret_answer(self, answer):
        """Set the secret answer hash"""
        self.secret_answer_hash = generate_password_hash(answer.lower())

    def check_secret_answer(self, answer):
        """Check if the provided answer matches the hash"""
        return check_password_hash(self.secret_answer_hash, answer.lower())
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def add_friend(self, user):
        """Add a friend relationship"""
        if not self.is_friend(user) and self.id != user.id:
            self.friends.append(user)
            return True
        return False
            
    def remove_friend(self, user):
        """Remove a friend relationship"""
        if self.is_friend(user):
            self.friends.remove(user)
            return True
        return False
    
    def is_friend(self, user):
        """Check if user is a friend"""
        return self.friends.filter(friendships.c.friend_id == user.id).count() > 0
    
    def get_all_friends(self):
        """Get all friends"""
        return self.friends.all()
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'last_login': self.last_login
        }

class WeeklyPlan(db.Model):
    __tablename__ = 'weekly_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    plan_name = db.Column(db.String(100), nullable=False)
    calorie_goal = db.Column(db.Integer, nullable=False)
    time_goal_minutes = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('weekly_plans', lazy=True))

class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    plan_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False)

    workout_type = db.Column(db.String(50), nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    intensity = db.Column(db.String(50), nullable=True)

    start_date = db.Column(db.Date, nullable=True)
    workout_days = db.Column(db.String(100), nullable=True)  # Comma-separated: "Mon,Tue,Wed"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('workout_logs', lazy=True))
