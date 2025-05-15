from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    secret_question = SelectField('Secret Question', choices=[
        ('first_pet', 'What was the name of your first pet?'),
        ('birth_city', 'In what city were you born?'),
        ('mother_maiden', "What is your mother's maiden name?"),
        ('first_school', 'What was the name of your first school?'),
        ('favorite_food', 'What is your favorite food?'),
    ], validators=[DataRequired()])
    
    secret_answer = StringField('Answer', validators=[DataRequired()])
    terms = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[DataRequired()])
    
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
