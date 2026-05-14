from flask import Flask
from flask import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf.csrf import CSRFProtect
from main.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migration = Migrate(app, db)
csrf = CSRFProtect(app)

from main import routes
from main import models
