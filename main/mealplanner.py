import random
from datetime import datetime
from flask import request, session


def get_recipes_for_meal(meal_type, saved_recipes):
    recipes = []

    for recipe in saved_recipes:
        if recipe["meal_type"] == meal_type:
            recipes.append(recipe)

    return recipes


def choose_recipe(meal_type, used_recipe_ids, saved_recipes):
    possible_recipes = get_recipes_for_meal(meal_type, saved_recipes)

    if len(possible_recipes) == 0:
        return None

    unused_recipes = []

    for recipe in possible_recipes:
        if recipe["id"] not in used_recipe_ids:
            unused_recipes.append(recipe)

    if len(unused_recipes) == 0:
        unused_recipes = possible_recipes

    selected_recipe = random.choice(unused_recipes)
    used_recipe_ids.append(selected_recipe["id"])

    return selected_recipe


def make_week_plan(days, meal_types, saved_recipes):
    week_plan = {}
    used_recipe_ids = []

    for day in days:
        week_plan[day] = {}

        for meal_type in meal_types:
            week_plan[day][meal_type] = choose_recipe(meal_type, used_recipe_ids, saved_recipes)

    return week_plan


def shuffle_single_day(current_plan, day, meal_types, saved_recipes):
    used_recipe_ids = []

    for plan_day in current_plan:
        if plan_day != day:
            for meal_type in current_plan[plan_day]:
                recipe = current_plan[plan_day][meal_type]

                if recipe is not None:
                    used_recipe_ids.append(recipe["id"])

    current_plan[day] = {}

    for meal_type in meal_types:
        current_plan[day][meal_type] = choose_recipe(meal_type, used_recipe_ids, saved_recipes)

    return current_plan


def get_plan_stats(week_plan, saved_recipes):
    meals_filled = 0
    quickest_recipe = None

    for day in week_plan:
        for meal_type in week_plan[day]:
            recipe = week_plan[day][meal_type]

            if recipe is not None:
                meals_filled += 1

                if quickest_recipe is None or recipe["time"] < quickest_recipe["time"]:
                    quickest_recipe = recipe
    
    if quickest_recipe is None:
        quickest_meal = "No meals yet"
    else: 
        quickest_meal = quickest_recipe["name"]

    return {
        "saved_count": len(saved_recipes),
        "meals_filled": meals_filled,
        "quickest_meal": quickest_meal,
        "planner_mode": "Weekly"
    }


def get_meal_planner_context(days, meal_types, saved_recipes, user):
    shuffle_type = request.args.get("shuffle")
    shuffle_day = request.args.get("day")

    if "meal_plan" not in session:
        session["meal_plan"] = make_week_plan(days, meal_types, saved_recipes)

    if shuffle_type == "week":
        session["meal_plan"] = make_week_plan(days, meal_types, saved_recipes)

    elif shuffle_type == "day" and shuffle_day in days:
        current_plan = session["meal_plan"]
        session["meal_plan"] = shuffle_single_day(current_plan, shuffle_day, meal_types, saved_recipes)

    stats = get_plan_stats(session["meal_plan"], saved_recipes)

    return {
        "page_title": "Plateful Meal Planner",
        "greeting": "Welcome back",
        "page_date": datetime.now().strftime("%A, %d %B %Y"),
        "initials": user["initials"],
        "display_name": user["display_name"],
        "username": user["username"],
        "days": days,
        "meal_types": meal_types,
        "week_plan": session["meal_plan"],
        "saved_recipes": saved_recipes,
        "stats": stats
    }
