# Fitness Tracker Web App

## Overview

This Fitness Tracker is a web application developed as part of the CITS5505 Agile Web Development project. It allows users to register, log their workouts, view progress visually, and track fitness goals efficiently—all within a responsive and interactive UI.

---

## Core Features

- Secure User Registration & Login (Flask-Login & Flask-WTF)
- Log workouts with type, duration, calories, and notes
- View progress using dynamic charts
- Share achievements (planned)
- Responsive, mobile-friendly dashboard UI
- CSRF-protected forms
- Unit & Selenium testing for key workflows

---

### **Team Members**

| Name                  | GitHub Username     | Student ID |
|-----------------------|---------------------|------------|
| Aneena Fernandez      | `FernandezAneena`   | 24302141   |
| Naishadh Kumar Vashik | `NaishadhKV`        | 24455506   |
| Winky Loong           | `wkk23`             | 24037833   |
| Zaid Sayed            | `zaidsayed`         | 23882963   |



## Tech Stack

- **Backend**: Flask (with Blueprint & Factory Pattern), SQLite, SQLAlchemy ORM  
- **Frontend**: HTML, CSS, Bootstrap, JavaScript, Jinja2 Templates  
- **Forms & Auth**: Flask-WTF, Flask-Login  
- **Data Visualization**: Chart.js  
- **Testing**: unittest, Selenium (with Headless Chrome)  
- **Version Control**: Git & GitHub  

---

## Project Structure

```
CITS5505-Exercise-Tracker-Project/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── forgot_password.html
│   │   ├── index.html
│   │   ├── login.html
│   │   └── register.html
│   ├── __init__.py
│   ├── blueprints.py
│   ├── config.py
│   ├── database.py
│   ├── dbase.db
│   ├── extensions.py
│   ├── forms.py
│   ├── routes.py
│   
│
├── env/                        # Virtual environment (ignored by Git)
├── instance/
│   └── dbase.db             # SQLite DB (auto-generated)
├── migrations/                 # Alembic migrations 
├── tests/                      # Unit/system tests
├── .gitignore
├── project-signup.py           # App runner script
└── README.md
```

---

## Setup Instructions


# 1. Clone the repository
git clone https://github.com/FernandezAneena/CITS5505-Exercise-Tracker-Project.git
cd fitness-tracker

# 2. Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate          # On Windows: env\Scripts\activate
```

# 3. Install dependencies

```bash
pip install -r requirements.txt
```

# 4. Set Flask app and initialize database

```bash
export FLASK_APP=projectsignup.py     # Windows CMD: set FLASK_APP=projectsignup.py
flask init-db
```

# 5. Run the application

```bash
python project-signup.py 
```

---

## Testing

### Unit Tests && Selenium Tests

```bash
python -m unittest discover -s tests -v  
```

---

## GitHub Workflow

- Use branches: `feature/login-form`, `feature-Selenium-Testing`, etc.
- Submit pull requests with clear descriptions
- Use GitHub Issues and Projects board for sprint planning
- Commit messages follow semantic conventions

---

## Sprint Progress

### ✅ Sprint 1
- [x] Project setup with Flask factory and Blueprints  
- [x] User registration & login with validation  
- [x] Workout logging backend model  
- [x] Workout plan creation &

### ✅ Sprint 2
- [x] Dashboard UI integration  
- [x] View logged workouts  
- [x] Data visualization with Chart.js  
- [x] Achievement sharing & social view  

### ⏳ Sprint 3 (Ongoing)
- [ ] updates CSRF-protected forms   
- [ ] Unit tests for auth and workout logic  
- [ ] Fixing backened and frontend bugs
- [ ] Full Selenium test coverage  

---

## License

This project is licensed under the MIT License.