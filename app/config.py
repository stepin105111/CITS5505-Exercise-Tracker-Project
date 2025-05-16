import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_database_uri

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'