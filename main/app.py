from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from form import LoginForm, RegisterForm
import os

from extensions import db
from routes.mealplanner import get_meal_planner_context

load_dotenv()

app = Flask(__name__)

# Core config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # NOSONAR — loaded from .env, not hardcoded

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plateful.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ---------- Auth ----------

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html', login_form=LoginForm(), signup_form=RegisterForm())

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['POST'])
def signup():
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        return redirect(url_for('login_page'))
    return render_template('forgot_password.html')


# ---------- Main pages ----------

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/my-recipes')
def my_recipes():
    return render_template('my_recipes.html')

@app.route('/saved')
def saved_recipes():
    return render_template('saved_recipe.html')

@app.route('/following')
def following():
    return render_template('following.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        return redirect(url_for('profile'))
    return render_template('settings.html')


@app.route('/meal-planner', methods=['GET'])
def meal_planner():
    days = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    meal_types = ["Breakfast", "Lunch", "Dinner"]

    saved_recipes = session.get("saved_recipes", [])

    user = {
        "initials": session.get("initials", "--"),
        "display_name": session.get("display_name", "Your Name"),
        "username": session.get("username", "@username")
    }

    context = get_meal_planner_context(days, meal_types, saved_recipes, user)

    return render_template('mealplanner.html', **context)

# ---------- Recipes ----------

@app.route('/upload', methods=['GET', 'POST'])
def upload_recipe():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('upload_recipe.html')

@app.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_details(recipe_id):
    return render_template('recipe_details.html', recipe_id=recipe_id)

@app.route('/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if request.method == 'POST':
        return redirect(url_for('recipe_details', recipe_id=recipe_id))
    return render_template('edit_recipe.html', recipe_id=recipe_id)

@app.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
def delete_recipe(recipe_id):
    return redirect(url_for('dashboard'))

@app.route('/recipe/<int:recipe_id>/save', methods=['POST'])
def save_recipe(recipe_id):
    return redirect(url_for('recipe_details', recipe_id=recipe_id))


# ---------- Static info pages ----------

@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')


# ---------- Errors ----------

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# ---------- Entry point ----------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)