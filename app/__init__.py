from flask import Flask
from app.config import Config
from flask.cli import with_appcontext
from app.extensions import db, login_manager, migrate  
from app.database import User
import click

@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('✅ Database initialized.')

def create_application(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.blueprints import blueprint
    app.register_blueprint(blueprint)
   
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.cli.add_command(init_db_command)

    return app