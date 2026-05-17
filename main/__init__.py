from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=[])

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from main.blueprints import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
