from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(30), nullable=True)
    biography = db.Column(db.String(500), nullable=True)
    joined_date   = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(200), nullable=True)

    recipes = db.relationship('Recipe', back_populates='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Will become a FK once the User model is added
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    author  = db.relationship('User', back_populates='recipes')

    title = db.Column(db.String(120), nullable=False)
    cuisine = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)

    prep_time = db.Column(db.String(20), nullable=True)
    servings = db.Column(db.Integer, nullable=True)

    description = db.Column(db.Text, nullable=True)
    # Stored as newline-separated text; use .ingredients_list / .steps_list to get a list
    ingredients = db.Column(db.Text, nullable=True)
    steps = db.Column(db.Text, nullable=True)

    image_filename = db.Column(db.String(200), nullable=True)
    meal_type = db.Column(db.String(30), nullable=True)

    @property
    def ingredients_list(self):
        if not self.ingredients:
            return []
        return [i for i in self.ingredients.split('\n') if i.strip()]

    @property
    def steps_list(self):
        if not self.steps:
            return []
        return [s for s in self.steps.split('\n') if s.strip()]

    def __repr__(self):
        return f"<Recipe {self.title}>"
