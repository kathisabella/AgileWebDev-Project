from flask import render_template, request, redirect, url_for, session

from main.forms import LoginForm, RegisterForm
from main import app, db
from main.mealplanner import get_meal_planner_context
from main.models import (
    User, 
    Recipe, 
    Ingredient, 
    RecipeStep, 
    SavedRecipe, 
    Follow,
    Activity,   
)

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required_redirect():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return None


def user_context(user=None):
    if user is None:
        user = get_current_user()

    if not user:
        return {
            "initials": "--",
            "display_name": "Your Name",
            "username": "@username",
        }

    return {
        "initials": user.display_name[:2].upper(),
        "display_name": user.display_name,
        "username": f"@{user.username}",
        "email": user.email,
        "bio": user.bio,
        "joined_date": user.joined_date.strftime("%Y") if user.joined_date else "",
    }



@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html', login_form=LoginForm(), signup_form=RegisterForm())

## -------- Login Page ---------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return redirect(url_for("login_page"))

    session["user_id"] = user.id
    session["username"] = user.username
    session["display_name"] = user.display_name
    session["initials"] = user.display_name[:2].upper()

    return redirect(url_for("dashboard"))

## -------- Sign Up Page ---------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    accept_terms = request.form.get("accept_terms")

    if not username or not email or not password or not accept_terms:
        return redirect(url_for("login_page"))

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return redirect(url_for("login_page"))

    display_name = f"{first_name} {last_name}".strip() or username

    new_user = User(
        username=username,
        email=email,
        display_name=display_name,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    session["username"] = new_user.username
    session["display_name"] = new_user.display_name
    session["initials"] = new_user.display_name[:2].upper()

    return redirect(url_for("dashboard"))

## -------- Dashboard ---------------------------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    recipe_count = Recipe.query.filter_by(author_id=user.id).count()
    saved_count = SavedRecipe.query.filter_by(user_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    total_saves = (
        db.session.query(SavedRecipe)
        .join(Recipe, SavedRecipe.recipe_id == Recipe.id)
        .filter(Recipe.author_id == user.id)
        .count()
    )

    return render_template(
        "dashboard.html",
        **user_context(user),
        greeting=f"Welcome, {user.display_name}",
        recipe_count=recipe_count,
        saved_count=saved_count,
        following_count=following_count,
        total_saves=total_saves,
    )

## -------- Explore Page ---------------------------------------------
@app.route("/explore", methods=["GET"])
def explore():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()

    return render_template(
        "explore.html",
        **user_context(),
        recipes=recipes,
    )

## -------- My Recipes Page ---------------------------------------------
@app.route("/my-recipes", methods=["GET"])
def my_recipes():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    recipes = Recipe.query.filter_by(author_id=user.id).order_by(Recipe.created_at.desc()).all()

    return render_template(
        "my_recipes.html",
        **user_context(user),
        recipes=recipes,
    )

## -------- Save Recipes Page ---------------------------------------------
@app.route("/saved", methods=["GET"])
def saved_recipes():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    saved_items = (
        SavedRecipe.query
        .filter_by(user_id=user.id)
        .order_by(SavedRecipe.saved_at.desc())
        .all()
    )

    recipes = [item.recipe for item in saved_items]

    return render_template(
        "saved_recipe.html",
        **user_context(user),
        recipes=recipes,
        saved_count=len(recipes),
    )

## -------- Log Out Page ---------------------------------------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))

## -------- Following Page ---------------------------------------------
@app.route("/following", methods=["GET"])
def following():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    following_rows = Follow.query.filter_by(follower_id=user.id).all()
    following_users = [row.following for row in following_rows]

    return render_template(
        "following.html",
        **user_context(user),
        following=following_users,
    )

## -------- Meal Planner Page ---------------------------------------------
@app.route("/meal-planner", methods=["GET"])
def meal_planner():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    days = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    meal_types = ["Breakfast", "Lunch", "Dinner"]

    saved_items = SavedRecipe.query.filter_by(user_id=user.id).all()

    saved_recipes = [
        {
            "name": saved.recipe.title,
            "meal_type": saved.recipe.meal_type or "Meal",
            "tag": saved.recipe.cuisine or "Recipe",
            "time": saved.recipe.prep_time or 0,
        }
        for saved in saved_items
    ]

    context = get_meal_planner_context(
        days,
        meal_types,
        saved_recipes,
        user_context(user),
    )

    return render_template("mealplanner.html", **context)

## -------- Profile Page ---------------------------------------------
@app.route("/profile", methods=["GET"])
def profile():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    recipe_count = Recipe.query.filter_by(author_id=user.id).count()
    saved_count = SavedRecipe.query.filter_by(user_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    followers_count = Follow.query.filter_by(following_id=user.id).count()

    total_saves = (
        db.session.query(SavedRecipe)
        .join(Recipe, SavedRecipe.recipe_id == Recipe.id)
        .filter(Recipe.author_id == user.id)
        .count()
    )

    activities = (
        Activity.query
        .filter_by(user_id=user.id)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    activity_feed = []

    for item in activities:
        if item.activity_type == "uploaded_recipe" and item.related_recipe:
            text = f"Uploaded recipe: {item.related_recipe.title}"
        elif item.activity_type == "saved_recipe" and item.related_recipe:
            text = f"Saved recipe: {item.related_recipe.title}"
        else:
            text = item.activity_type

        activity_feed.append({
            "text": text,
            "time": item.created_at.strftime("%d %b %Y")
        })

    return render_template(
        "profile.html",
        **user_context(user),
        recipe_count=recipe_count,
        saved_count=saved_count,
        following_count=following_count,
        followers_count=followers_count,
        total_saves=total_saves,
        activity=activity_feed,
    )

## -------- Settings Page ---------------------------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    if request.method == "POST":
        user.display_name = request.form.get("display_name", "").strip() or user.display_name
        user.username = request.form.get("username", "").strip() or user.username
        user.email = request.form.get("email", "").strip().lower() or user.email
        user.bio = request.form.get("bio", "").strip()

        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password and new_password == confirm_password:
            user.set_password(new_password)

        db.session.commit()

        session["username"] = user.username
        session["display_name"] = user.display_name
        session["initials"] = user.display_name[:2].upper()

        return redirect(url_for("profile"))

    return render_template("settings.html", **user_context(user))

## -------- Upload Recipe Page ---------------------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload_recipe():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        cuisine = request.form.get("cuisine", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        prep_time = request.form.get("prep_time", "").strip()
        servings = request.form.get("servings", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            return redirect(url_for("upload_recipe"))

        recipe = Recipe(
            author_id=user.id,
            title=title,
            cuisine=cuisine,
            difficulty=difficulty,
            prep_time=int(prep_time) if prep_time.isdigit() else None,
            servings=int(servings) if servings.isdigit() else None,
            description=description,
        )

        db.session.add(recipe)
        db.session.commit()

        ingredients = request.form.getlist("ingredients")
        for ingredient_name in ingredients:
            ingredient_name = ingredient_name.strip()
            if ingredient_name:
                db.session.add(
                    Ingredient(
                        recipe_id=recipe.id,
                        name=ingredient_name,
                    )
                )

        steps = request.form.getlist("steps")
        for index, instruction in enumerate(steps, start=1):
            instruction = instruction.strip()
            if instruction:
                db.session.add(
                    RecipeStep(
                        recipe_id=recipe.id,
                        step_number=index,
                        instruction=instruction,
                    )
                )

        db.session.add(
            Activity(
                user_id=user.id,
                activity_type="uploaded_recipe",
                related_recipe_id=recipe.id,
            )
        )

        db.session.commit()

        return redirect(url_for("recipe_details", recipe_id=recipe.id))

    return render_template("upload_recipe.html", **user_context(user))

## -------- Recipe Details Page ---------------------------------------------
@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def recipe_details(recipe_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    recipe = Recipe.query.get_or_404(recipe_id)

    return render_template(
        "recipe_details.html",
        **user_context(),
        recipe=recipe,
        recipe_id=recipe.id,
    )

## -------- Edit Recipe Page ---------------------------------------------
@app.route("/recipe/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.author_id != user.id:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        recipe.title = request.form.get("title", "").strip() or recipe.title
        recipe.cuisine = request.form.get("cuisine", "").strip()
        recipe.difficulty = request.form.get("difficulty", "").strip()
        recipe.description = request.form.get("description", "").strip()

        prep_time = request.form.get("prep_time", "").strip()
        servings = request.form.get("servings", "").strip()

        recipe.prep_time = int(prep_time) if prep_time.isdigit() else None
        recipe.servings = int(servings) if servings.isdigit() else None

        Ingredient.query.filter_by(recipe_id=recipe.id).delete()
        RecipeStep.query.filter_by(recipe_id=recipe.id).delete()

        ingredients = request.form.getlist("ingredients")
        for ingredient_name in ingredients:
            ingredient_name = ingredient_name.strip()
            if ingredient_name:
                db.session.add(Ingredient(recipe_id=recipe.id, name=ingredient_name))

        steps = request.form.getlist("steps")
        for index, instruction in enumerate(steps, start=1):
            instruction = instruction.strip()
            if instruction:
                db.session.add(
                    RecipeStep(
                        recipe_id=recipe.id,
                        step_number=index,
                        instruction=instruction,
                    )
                )

        db.session.commit()
        return redirect(url_for("recipe_details", recipe_id=recipe.id))

    return render_template(
        "edit_recipe.html",
        **user_context(user),
        recipe=recipe,
        recipe_id=recipe.id,
    )

## -------- Delete Recipe Page ---------------------------------------------
@app.route("/recipe/<int:recipe_id>/delete", methods=["POST"])
def delete_recipe(recipe_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.author_id != user.id:
        return redirect(url_for("dashboard"))

    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for("my_recipes"))

## -------- Save Recipe Page ---------------------------------------------
@app.route("/recipe/<int:recipe_id>/save", methods=["POST"])
def save_recipe(recipe_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    recipe = Recipe.query.get_or_404(recipe_id)

    existing_save = SavedRecipe.query.filter_by(
        user_id=user.id,
        recipe_id=recipe.id,
    ).first()

    if not existing_save:
        db.session.add(
            SavedRecipe(
                user_id=user.id,
                recipe_id=recipe.id,
            )
        )

        db.session.add(
            Activity(
                user_id=user.id,
                activity_type="saved_recipe",
                related_recipe_id=recipe.id,
            )
        )

        db.session.commit()

    return redirect(url_for("recipe_details", recipe_id=recipe.id))

## -------- Forgot Password Page ---------------------------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        return redirect(url_for("login_page"))
    return render_template("forgot_password.html")

## -------- Terms & Conditions Page ---------------------------------------------
@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

## -------- Privacy Page ---------------------------------------------
@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')

## -------- 404 Error Handling Page ---------------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
