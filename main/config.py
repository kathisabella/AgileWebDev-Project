import os
from dotenv import load_dotenv
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYAPP_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'plateful.db')

class TestConfig(Config):
    SECRET_KEY = 'unit-test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    WTF_CSRF_ENABLED = False

class SeleniumTestConfig(Config):
    SECRET_KEY = 'selenium-test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///selenium_test.db'
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False

