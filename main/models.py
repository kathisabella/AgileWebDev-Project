from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

from main import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    joined_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    profile_image_url = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    ## relationships
    recipes = db.relationship("Recipe", backref="author", lazy=True)
    saved_recipes = db.relationship("SavedRecipe", backref="user", lazy=True)
    meal_plan_entries = db.relationship("MealPlanEntry", backref="user", lazy=True)

class Recipe(db.Model):
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cuisine = db.Column(db.String(80), nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)
    servings = db.Column(db.Integer, nullable=True)
    meal_type = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    ## relationships
    ingredients = db.relationship("Ingredient", backref="recipe", lazy=True)
    steps = db.relationship("RecipeStep", backref="recipe", lazy=True)
    saved_by = db.relationship("SavedRecipe", backref="recipe", lazy=True)
    meal_plan_entries = db.relationship("MealPlanEntry", backref="recipe", lazy=True)

class Ingredient(db.Model):
    __tablename__ = "ingredient"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Numeric(8, 2), nullable=True)
    unit = db.Column(db.String(50), nullable=True)


class RecipeStep(db.Model):
    __tablename__ = "recipe_step"
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)


class SavedRecipe(db.Model):
    __tablename__ = "saved_recipe"

    __table_args__ = (db.UniqueConstraint("user_id", "recipe_id", name="unique_saved_recipe"), )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    saved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class MealPlanEntry(db.Model):
    __tablename__ = "meal_plan_entry"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=True)

    day = db.Column(db.String(20), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)


class Follow(db.Model):
    __tablename__ = "follow"

    __table_args__ = (db.UniqueConstraint("follower_id", "following_id", name="unique_follow"), )

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    followed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ## relationships 
    follower = db.relationship("User", foreign_keys=[follower_id])
    following = db.relationship("User", foreign_keys=[following_id])


class Activity(db.Model):
    __tablename__ = "activity"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    activity_type = db.Column(db.String(50), nullable=False)
    related_recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=True)
    related_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ## relationships
    user = db.relationship("User", foreign_keys=[user_id])
    related_recipe = db.relationship("Recipe", foreign_keys=[related_recipe_id])
    related_user = db.relationship("User", foreign_keys=[related_user_id])
