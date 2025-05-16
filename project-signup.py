from flask_migrate import Migrate
from app import create_application
from app.config import Config 
from app.extensions import db

if __name__ == "__main__":
    application = create_application(Config)
    migrate = Migrate(application, db)
    application.run(debug=True, use_debugger=False, use_reloader=False)