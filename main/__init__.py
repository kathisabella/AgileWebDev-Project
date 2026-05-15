from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()

csrf = CSRFProtect() 

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    csrf.init_app(app)

    from main.blueprints import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
