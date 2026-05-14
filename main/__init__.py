from flask import Flask
from flask import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from main.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migration = Migrate(app, db)
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

from main import routes
from main import models
