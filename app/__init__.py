from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate  
from app.database import User

def create_application(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.blueprints import blueprint
    app.register_blueprint(blueprint)
    
    # Register the user_loader function here
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app




