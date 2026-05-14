import os
import uuid
from datetime import date
from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy import func
from werkzeug.utils import secure_filename

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

_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

def _save_image(file):
    """Save an uploaded file to static/uploads and return the URL path, or None."""
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(_UPLOAD_FOLDER, filename))
    return f"uploads/{filename}"


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
        "id": user.id,
        "initials": user.display_name[:2].upper(),
        "display_name": user.display_name,
        "username": f"@{user.username}",
        "email": user.email,
        "bio": user.bio,
        "joined_date": user.joined_date.strftime("%Y") if user.joined_date else "",
    }



@app.route('/', methods=['GET'])
def login_page():
    active_tab = request.args.get("tab", "login")
    return render_template('login.html', login_form=LoginForm(), signup_form=RegisterForm(), active_tab=active_tab)

## -------- Login Page ---------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        flash("Invalid email or password.", "login_error")
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
        flash("Please fill in all required fields and accept the terms.", "signup_error")
        return redirect(url_for("login_page", tab="signup"))

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "signup_error")
        else:
            flash("An account with that email already exists.", "signup_error")
        return redirect(url_for("login_page", tab="signup"))

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

_TIPS = [
    "Salt your pasta water until it tastes like the sea — it's your only chance to season the pasta itself.",
    "Pat meat dry before searing. Moisture is the enemy of a good crust.",
    "Taste as you go. Seasoning at the end can't fix under-seasoned layers.",
    "Rest your meat after cooking — 5 minutes makes a big difference in juiciness.",
    "Cold butter whisked into a sauce at the end gives it a glossy, restaurant finish.",
    "Toast your spices in a dry pan before grinding to unlock deeper flavour.",
    "Acid (lemon, vinegar) added at the end brightens a dish that tastes flat.",
    "Use the pasta cooking water to loosen and bind your sauce — the starch is key.",
    "Room-temperature eggs and dairy incorporate more evenly into batters.",
    "A pinch of sugar balances acidic tomato sauces without making them sweet.",
    "Slice meat against the grain to shorten muscle fibres and make it more tender.",
    "Fresh herbs go in at the end; dried herbs go in early so they have time to bloom.",
]


def _daily_tip():
    return _TIPS[date.today().timetuple().tm_yday % len(_TIPS)]


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

    recent_saved = [
        item.recipe for item in (
            SavedRecipe.query
            .filter_by(user_id=user.id)
            .order_by(SavedRecipe.saved_at.desc())
            .limit(3)
            .all()
        )
    ]

    top_recipes_raw = (
        db.session.query(Recipe, func.count(SavedRecipe.id).label("save_count"))
        .outerjoin(SavedRecipe, SavedRecipe.recipe_id == Recipe.id)
        .filter(Recipe.author_id == user.id)
        .group_by(Recipe.id)
        .order_by(func.count(SavedRecipe.id).desc())
        .limit(5)
        .all()
    )
    top_recipes = [{"recipe": r, "save_count": count} for r, count in top_recipes_raw]

    followed_users = [
        f.following for f in (
            Follow.query
            .filter_by(follower_id=user.id)
            .order_by(Follow.followed_at.desc())
            .limit(5)
            .all()
        )
    ]

    raw_activity = (
        Activity.query
        .filter_by(user_id=user.id)
        .order_by(Activity.created_at.desc())
        .limit(5)
        .all()
    )
    activity_feed = []
    for item in raw_activity:
        if item.activity_type == "uploaded_recipe" and item.related_recipe:
            text = f"Uploaded recipe: {item.related_recipe.title}"
        elif item.activity_type == "saved_recipe" and item.related_recipe:
            text = f"Saved recipe: {item.related_recipe.title}"
        else:
            text = item.activity_type
        activity_feed.append({"text": text, "time": item.created_at.strftime("%d %b %Y")})

    return render_template(
        "dashboard.html",
        **user_context(user),
        greeting=f"Welcome, {user.display_name}",
        recipe_count=recipe_count,
        saved_count=saved_count,
        following_count=following_count,
        total_saves=total_saves,
        recent_saved=recent_saved,
        top_recipes=top_recipes,
        activity_feed=activity_feed,
        tip=_daily_tip(),
        followed_users=followed_users,
        page_date=date.today().strftime("%A, %d %B %Y"),
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

## -------- Follow / Unfollow ---------------------------------------------
@app.route("/follow/<int:user_id>", methods=["POST"])
def follow_user(user_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    if user.id != user_id:
        already = Follow.query.filter_by(follower_id=user.id, following_id=user_id).first()
        if not already:
            db.session.add(Follow(follower_id=user.id, following_id=user_id))
            db.session.commit()

    return redirect(request.referrer or url_for("following"))


@app.route("/unfollow/<int:user_id>", methods=["POST"])
def unfollow_user(user_id):
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()
    follow = Follow.query.filter_by(follower_id=user.id, following_id=user_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()

    return redirect(request.referrer or url_for("following"))

## -------- Meal Planner Page ---------------------------------------------
@app.route("/meal-planner", methods=["GET"])
def meal_planner():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user = get_current_user()

    meal_types = ["Breakfast", "Lunch", "Dinner"]

    days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]

    saved_items = SavedRecipe.query.filter_by(user_id=user.id).all()

    saved_recipes = [
        {
            "id": saved.recipe.id,
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

    following_rows = Follow.query.filter_by(follower_id=user.id).all()
    followers_rows = Follow.query.filter_by(following_id=user.id).all()
    following_count = len(following_rows)
    followers_count = len(followers_rows)

    following_id_set = {row.following_id for row in following_rows}

    followers_list = [
        {
            "id": row.follower.id,
            "username": row.follower.username,
            "display_name": row.follower.display_name,
            "initials": row.follower.display_name[:2].upper(),
            "is_following": row.follower_id in following_id_set,
        }
        for row in followers_rows
    ]

    following_list = [
        {
            "id": row.following.id,
            "username": row.following.username,
            "display_name": row.following.display_name,
            "initials": row.following.display_name[:2].upper(),
        }
        for row in following_rows
    ]

    total_saves = (
        db.session.query(SavedRecipe)
        .join(Recipe, SavedRecipe.recipe_id == Recipe.id)
        .filter(Recipe.author_id == user.id)
        .count()
    )

    recipes = (
        Recipe.query
        .filter_by(author_id=user.id)
        .order_by(Recipe.created_at.desc())
        .all()
    )

    saved_recipes = [
        item.recipe for item in (
            SavedRecipe.query
            .filter_by(user_id=user.id)
            .order_by(SavedRecipe.saved_at.desc())
            .all()
        )
    ]

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
        followers=followers_list,
        following_users=following_list,
        total_saves=total_saves,
        activity=activity_feed,
        recipes=recipes,
        saved_recipes=saved_recipes,
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
        meal_type = request.form.get("meal_type", "").strip()
        prep_time = request.form.get("prep_time", "").strip()
        servings = request.form.get("servings", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            return redirect(url_for("upload_recipe"))

        image_url = _save_image(request.files.get("image"))

        recipe = Recipe(
            author_id=user.id,
            title=title,
            cuisine=cuisine,
            difficulty=difficulty,
            meal_type=meal_type or None,
            prep_time=int(prep_time) if prep_time.isdigit() else None,
            servings=int(servings) if servings.isdigit() else None,
            description=description,
            image_url=image_url,
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
        recipe.meal_type = request.form.get("meal_type", "").strip() or None
        recipe.description = request.form.get("description", "").strip()

        new_image = _save_image(request.files.get("image"))
        if new_image:
            recipe.image_url = new_image

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
