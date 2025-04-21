
# Exercise Tracker Web App

## Overview

This is a web-based Exercise Tracker built as part of an Agile Web Development project. The application enables users to register/login, log their workouts, view progress through charts, and selectively share achievements with others.

---

## Features

- User Registration & Login
- Log daily exercise sessions (type, duration, calories, notes)
- View progress through interactive charts
- Share achievements with selected users
- Responsive and intuitive UI

---

##  Team Members

- Winky Loong
- Naishadh Kumar Vashik
- Zaid Sayed
- Aneena Fernandez

---

## 🛠️ Tech Stack

- **Backend**: Flask (Python), SQLite (SQLAlchemy ORM)
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Data Visualization**: Chart.js (optional)
- **Version Control**: Git & GitHub


## 📁 Project Structure

CITS5505-Exercise-Tracker-Project/
├── app/
│   ├── app.py                # Main Flask app and route handling
│   ├── database.py           # SQLAlchemy setup and DB helper functions
│   ├── model.py              # (Optional) Models for User, Workout, etc.
│   ├── forms.py              # (Optional) WTForms (if used)
│   ├── routes.py             # (Optional) Route separation
│   ├── static/
│   │   ├── css/
│   │   │   ├── login-style.css
│   │   │   └── style.css
│   │   └── js/
│   │       └── (optional JS files)
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       └── register.html
│
├── instance/
│   └── database.db           # SQLite DB (auto-generated after init)
│
├── env/                      # Python virtual environment (excluded from Git)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation


## 🧪 Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/your-org/exercise-tracker.git
cd exercise-tracker

# 2. Create a virtual environment
python3 -m venv env
source env/bin/activate          # Windows: env\Scripts\activate

# 3. Set Flask app (adjust if app.py is outside 'app/' folder)
export FLASK_APP=app.app         # Windows CMD: set FLASK_APP=app.app
flask init-db                    # Creates SQLite tables

# 4. Launch the development server
flask run


## 📋 GitHub Workflow

- Feature branches: `feature/login`, `feature/register`, etc.
- Pull requests with detailed descriptions
- Use Issues and Project Board for sprint tasks
- Regular commits with proper messages

---

## ✅ Sprint 1 Task Summary

- [ ] Landing Page UI
- [ ] Login/Register UI
- [ ] Backend Login/Register APIs
- [ ] Link frontend and backend
- [ ] Create repo and initial structure

---

## 📄 License

This project is licensed under the MIT License.
