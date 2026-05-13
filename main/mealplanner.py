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


def make_one_day_plan(current_plan, meal_types, saved_recipes):
    used_recipe_ids = []

    for plan_day in current_plan:
        for meal_type in current_plan[plan_day]:
            recipe = current_plan[plan_day][meal_type]

            if recipe is not None:
                used_recipe_ids.append(recipe["id"])

    one_day_plan = {}

    for meal_type in meal_types:
        one_day_plan[meal_type] = choose_recipe(meal_type, used_recipe_ids, saved_recipes)

    return one_day_plan

def delete_day_and_reorder(current_plan, day_to_delete):
    if day_to_delete in current_plan:
        current_plan.pop(day_to_delete)

    old_day_plans = list(current_plan.values())
    new_plan = {}

    for index, day_plan in enumerate(old_day_plans, start=1):
        new_plan[f"Day {index}"] = day_plan

    return new_plan

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
    }


def get_meal_planner_context(days, meal_types, saved_recipes, user):
    action = request.args.get("action")
    day_to_delete = request.args.get("day")

    if "meal_plan" not in session:
        session["meal_plan"] = {}

    current_plan = session["meal_plan"]

    if action == "shuffle_day":
        if len(current_plan) < 7:
            next_day = f"Day {len(current_plan) + 1}"
            current_plan[next_day] = make_one_day_plan(current_plan, meal_types, saved_recipes)
            session["meal_plan"] = current_plan
            session.modified = True

    elif action == "delete_day":
        session["meal_plan"] = delete_day_and_reorder(current_plan, day_to_delete)
        session.modified = True

    elif action == "clear_all":
        session["meal_plan"] = {}
        session.modified = True

    stats = get_plan_stats(session["meal_plan"], saved_recipes)

    generated_days = list(session["meal_plan"].keys())

    if len(generated_days) == 0:
        display_days = ["Day 1"]
    else:
        display_days = generated_days

    return {
        "page_title": "Plateful Meal Planner",
        "greeting": "Welcome back",
        "page_date": datetime.now().strftime("%A, %d %B %Y"),
        "initials": user["initials"],
        "display_name": user["display_name"],
        "username": user["username"],
        "days": days,
        "display_days": display_days,
        "generated_days": generated_days,
        "meal_types": meal_types,
        "week_plan": session["meal_plan"],
        "saved_recipes": saved_recipes,
        "stats": stats
    }
