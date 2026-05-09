from flask import render_template, request, redirect, url_for, session
from main import app
from main.mealplanner import get_meal_planner_context

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['POST'])
def signup():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/explore', methods=['GET'])
def explore():
    return render_template('explore.html')

@app.route('/my-recipes', methods=['GET'])
def my_recipes():
    return render_template('my_recipes.html')

@app.route('/saved', methods=['GET'])
def saved_recipes():
    return render_template('saved_recipe.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/following', methods=['GET'])
def following():
    return render_template('following.html')

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

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        return redirect(url_for('profile'))
    return render_template('settings.html')

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

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        return redirect(url_for('login_page'))
    return render_template('forgot_password.html')

@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
