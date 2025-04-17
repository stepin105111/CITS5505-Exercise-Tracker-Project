from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, InputRequired, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
# Correctly set configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    email= db.Column(db.String(20), primary_key=True)
    # Correctly set the length of the name and password fields
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    
    
class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    email = StringField(validators=[InputRequired(), Email(), Length(max=20)], render_kw={"placeholder": "Email"})
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists. Please use a different email.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    form=LoginForm()
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', form=form, error="An error occurred while creating your account. Please try again.")
    
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
