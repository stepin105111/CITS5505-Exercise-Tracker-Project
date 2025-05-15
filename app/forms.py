from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    TextAreaField,
    IntegerField,
    DateField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    NumberRange,
    Optional,
)


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=50)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )

    secret_question = SelectField(
        "Secret Question",
        choices=[
            ("first_pet", "What was the name of your first pet?"),
            ("birth_city", "In what city were you born?"),
            ("mother_maiden", "What is your mother's maiden name?"),
            ("first_school", "What was the name of your first school?"),
            ("favorite_food", "What is your favorite food?"),
        ],
        validators=[DataRequired()],
    )

    secret_answer = StringField("Answer", validators=[DataRequired()])
    terms = BooleanField(
        "I agree to the Terms of Service and Privacy Policy",
        validators=[DataRequired()],
    )

    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class WorkoutPlanForm(FlaskForm):
    plan_name = StringField("Plan Name", validators=[DataRequired(), Length(max=100)])
    calorie_goal = TextAreaField("Calories to Burn (week)", validators=[DataRequired()])
    time_goal_minutes = IntegerField(
        "Duration in minutes (weeks)", validators=[DataRequired(), NumberRange(min=1)]
    )
    submit = SubmitField("Create Plan")


class WorkoutLogForm(FlaskForm):
    plan_name = StringField("Workout Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    duration_minutes = IntegerField("Duration (minutes)", validators=[DataRequired()])
    workout_type = SelectField(
        "Workout Type",
        choices=[
            ("", "-- Select --"),
            ("Cardio", "Cardio"),
            ("Strength", "Strength"),
            ("Running", "Running"),
            ("Cycling", "Cycling"),
            ("Yoga", "Yoga"),
            ("Mixed", "Mixed"),
        ],
        validators=[DataRequired()],
    )
    calories = IntegerField("Calories", validators=[Optional()])
    intensity = SelectField(
        "Intensity",
        choices=[
            ("", "-- Select Intensity --"),
            ("Low", "Low"),
            ("Moderate", "Moderate"),
            ("High", "High"),
        ],
        validators=[Optional()],
    )
    start_date = DateField("Start Date", validators=[Optional()])
    workout_days = StringField("Workout Days", validators=[Optional()])
    submit = SubmitField("Create Workout")
