from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from app.forms import LoginForm, RegisterForm, WorkoutPlanForm, WorkoutLogForm
from app.forms import ForgotUsernameForm, SecurityAnswerForm, ResetPasswordForm
import os
from app.extensions import db
from app.database import User, WeeklyPlan, WorkoutLog, friendships
from datetime import datetime
from flask.cli import with_appcontext
from flask_migrate import Migrate
import click
from datetime import timedelta
from collections import Counter
from collections import defaultdict
import random
from app.blueprints import blueprint 


@blueprint.route("/")
def index():
    return render_template("index.html")

@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        secret_question = form.secret_question.data
        secret_answer = form.secret_answer.data

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "register.html", form=form, error="Username already exists"
            )
        if existing_email:
            return render_template(
                "register.html", form=form, error="Email already registered"
            )

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.secret_question = secret_question
        new_user.set_secret_answer(secret_answer)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            db.session.rollback()
            return render_template(
                "register.html", form=form, error=f"Error creating account: {str(e)}"
            )

    return render_template("register.html", form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password", "error")
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@blueprint.route("/about")
def about():
    return render_template("about.html")


@blueprint.route("/home")
def home():
    return render_template("index.html")


from app.forms import ForgotUsernameForm, SecurityAnswerForm 

@blueprint.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ForgotUsernameForm()

    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user and user.secret_question:
            question_texts = {
                "first_pet": "What was the name of your first pet?",
                "birth_city": "In what city were you born?",
                "mother_maiden": "What is your mother's maiden name?",
                "first_school": "What was the name of your first school?",
                "favorite_food": "What is your favorite food?",
            }
            question_text = question_texts.get(user.secret_question, user.secret_question)

            return render_template(
                "forgot_password.html",
                step="security_question",
                username=username,
                security_question=question_text,
                form=SecurityAnswerForm()
            )
        else:
            return render_template(
                "forgot_password.html",
                step="username",
                form=form,
                error="Username not found or no security question set",
            )

    return render_template("forgot_password.html", step="username", form=form)



@blueprint.route("/verify-answer", methods=["POST"])
def verify_answer():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = SecurityAnswerForm()

    if form.validate_on_submit():
        username = form.username.data
        answer = form.answer.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_secret_answer(answer):
            return render_template(
                "forgot_password.html",
                step="reset_password",
                username=username,
                form=ResetPasswordForm()
            )
        else:
            question_texts = {
                "first_pet": "What was the name of your first pet?",
                "birth_city": "In what city were you born?",
                "mother_maiden": "What is your mother's maiden name?",
                "first_school": "What was the name of your first school?",
                "favorite_food": "What is your favorite food?",
            }
            question_text = question_texts.get(user.secret_question, user.secret_question) if user else ""

            return render_template(
                "forgot_password.html",
                step="security_question",
                username=username,
                security_question=question_text,
                form=form,
                error="Incorrect answer. Please try again."
            )

    # If form did not validate (shouldn't happen unless tampered)
    return redirect(url_for("main.forgot_password"))

@blueprint.route("/reset-password", methods=["POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        username = form.username.data
        new_password = form.new_password.data

        user = User.query.filter_by(username=username).first()

        if user:
            try:
                user.set_password(new_password)
                db.session.commit()
                flash("Password has been reset. Please login with your new password.", "success")
                return redirect(url_for("main.login"))
            except Exception as e:
                db.session.rollback()
                return render_template(
                    "forgot_password.html",
                    step="reset_password",
                    username=username,
                    form=form,
                    error=f"An error occurred: {str(e)}"
                )
        else:
            return render_template(
                "forgot_password.html",
                step="username",
                form=ResetPasswordForm(),
                error="User not found"
            )

    # If validation failed (e.g., mismatched or short password), re-render form with errors
    return render_template(
        "forgot_password.html",
        step="reset_password",
        username=form.username.data,
        form=form
    )

@blueprint.route("/dashboard")
@login_required
def dashboard():
    user = current_user
    form_plan = WorkoutPlanForm()
    form_log = WorkoutLogForm()

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
            days = [day.strip() for day in log.workout_days.split(",")]
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
            for day in log.workout_days.split(","):
                weekday_calories[day.strip()] += log.calories

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    sorted_weekdays = [day for day in weekday_order if day in weekday_calories]
    calories_by_weekday = [weekday_calories[day] for day in sorted_weekdays]

    # 🟪 Line chart: Time spent per weekday (NEW)
    weekday_time_spent = defaultdict(int)
    for log in workout_logs:
        if log.workout_days and log.duration_minutes:
            for day in log.workout_days.split(","):
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

        progress_percent = min(
            (calorie_ratio + time_ratio) / 2 * 100, 100
        )  # Cap at 100%
        progress_data[plan.plan_name] = round(progress_percent, 1)

    # Get current user's recent workout
    user_recent_log = (
        WorkoutLog.query.filter_by(user_id=user.id)
        .order_by(WorkoutLog.created_at.desc())
        .first()
    )

    # Friend data for share section
    friends = user.get_all_friends()

    # Get real workout data for each friend and include current user
    leaderboard_data = []

    # Add current user's data
    if user_recent_log:
        days_ago = (datetime.utcnow() - user_recent_log.created_at).days
        leaderboard_data.append(
            {
                "username": user.username + " (You)",
                "activity": user_recent_log.workout_type,
                "calories": user_recent_log.calories or 0,
                "duration": user_recent_log.duration_minutes,
                "shared_days_ago": days_ago,
                "is_current_user": True,
            }
        )
    else:
        leaderboard_data.append(
            {
                "username": user.username + " (You)",
                "activity": "No recent activity",
                "calories": 0,
                "duration": 0,
                "shared_days_ago": None,
                "is_current_user": True,
            }
        )

    # Add friends data
    for friend in friends:
        # Find the most recent workout log for this friend
        recent_log = (
            WorkoutLog.query.filter_by(user_id=friend.id)
            .order_by(WorkoutLog.created_at.desc())
            .first()
        )

        if recent_log:
            # Calculate days ago
            days_ago = (datetime.utcnow() - recent_log.created_at).days

            # Add friend with their actual workout data
            leaderboard_data.append(
                {
                    "username": friend.username,
                    "activity": recent_log.workout_type,
                    "calories": recent_log.calories or 0,
                    "duration": recent_log.duration_minutes,
                    "shared_days_ago": days_ago,
                    "is_current_user": False,
                }
            )
        else:
            # Friend has no workout logs yet
            leaderboard_data.append(
                {
                    "username": friend.username,
                    "activity": "No recent activity",
                    "calories": 0,
                    "duration": 0,
                    "shared_days_ago": None,
                    "is_current_user": False,
                }
            )

    # Sort everyone by calories burned (highest first)
    leaderboard_data = sorted(
        leaderboard_data, key=lambda x: x["calories"], reverse=True
    )

    # Add ranking position
    for i, person_data in enumerate(leaderboard_data):
        person_data["rank"] = i + 1

    # Set these in the context for rendering
    friends_data = leaderboard_data
    has_friends = len(friends) > 0

    return render_template(
        "dashboard.html",
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
        progress_data=progress_data,
        friends=friends_data,
        form_plan=form_plan,
        form_log=form_log,
    )


@blueprint.route("/create_plan", methods=["POST"])
@login_required
def create_plan():
    form = WorkoutPlanForm()

    if form.validate_on_submit():
        try:
            new_plan = WeeklyPlan(
                user_id=current_user.id,
                plan_name=form.plan_name.data,
                calorie_goal=form.calorie_goal.data,
                time_goal_minutes=form.time_goal_minutes.data,
            )
            db.session.add(new_plan)
            db.session.commit()
            flash("Workout plan created successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating plan: {str(e)}", "danger")
    else:
        flash("Please fill out all required fields correctly.", "danger")

    return redirect(url_for("main.dashboard"))


from app.forms import WorkoutLogForm


@blueprint.route("/create_workout", methods=["GET", "POST"])
@login_required
def create_workout():
    form = WorkoutLogForm()

    if form.validate_on_submit():
        try:
            workout = WorkoutLog(
                user_id=current_user.id,
                plan_name=form.plan_name.data,
                description=form.description.data,
                duration_minutes=form.duration_minutes.data,
                workout_type=form.workout_type.data,
                calories=form.calories.data or 0,
                intensity=form.intensity.data,
                start_date=form.start_date.data,
                workout_days=form.workout_days.data,
            )
            db.session.add(workout)
            db.session.commit()
            flash("Workout logged successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error logging workout: {str(e)}", "danger")

        return redirect(url_for("main.dashboard"))


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.login"))


@blueprint.route("/delete_plan/<int:plan_id>", methods=["POST"])
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

    return redirect(url_for("main.dashboard"))


@blueprint.route("/reset_stats", methods=["POST"])
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

    return redirect(url_for("main.dashboard"))


# Friend search and add functionality
@blueprint.route("/search-users", methods=["GET"])
@login_required
def search_users():

    query = request.args.get("query", "")

    if not query or len(query) < 2:
        return jsonify({"users": []})

    # Find users with usernames containing the query
    users = (
        User.query.filter(User.username.like(f"%{query}%"), User.id != current_user.id)
        .limit(10)
        .all()
    )

    # Format results with friendship status
    results = []
    for user in users:
        results.append(
            {
                "id": user.id,
                "username": user.username,
                "is_friend": current_user.is_friend(user),
            }
        )

    return jsonify({"users": results})


@blueprint.route("/add-friend", methods=["POST"])
@login_required
def add_friend():

    friend_username = request.json.get("username")

    if not friend_username:
        return jsonify({"error": "No username provided"}), 400

    friend = User.query.filter_by(username=friend_username).first()

    if not friend:
        return jsonify({"error": "User not found"}), 404

    if current_user.id == friend.id:
        return jsonify({"error": "Cannot add yourself as a friend"}), 400

    if current_user.is_friend(friend):
        return jsonify({"error": "Already friends with this user"}), 400

    try:
        success = current_user.add_friend(friend)
        db.session.commit()

        if success:
            return jsonify({"message": f"Added {friend.username} as a friend"})
        else:
            return jsonify({"error": "Failed to add friend"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error adding friend: {str(e)}"}), 500


@blueprint.route("/remove-friend", methods=["POST"])
@login_required
def remove_friend():

    friend_username = request.json.get("username")

    if not friend_username:
        return jsonify({"error": "No username provided"}), 400

    friend = User.query.filter_by(username=friend_username).first()

    if not friend:
        return jsonify({"error": "User not found"}), 404

    if not current_user.is_friend(friend):
        return jsonify({"error": "Not friends with this user"}), 400

    try:
        success = current_user.remove_friend(friend)
        db.session.commit()

        if success:
            return jsonify({"message": f"Removed {friend.username} from friends"})
        else:
            return jsonify({"error": "Failed to remove friend"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error removing friend: {str(e)}"}), 500