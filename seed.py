from main import app, db
from main.models import User, Recipe, Ingredient, RecipeStep, SavedRecipe, Follow, Activity

USERS = [
    {
        "username": "demo",
        "email": "demo@plateful.com",
        "password": "demo1234",
        "display_name": "Demo User",
        "bio": "Just here to try out Plateful and find great recipes.",
    },
    {
        "username": "alicecooks",
        "email": "alice@plateful.com",
        "password": "alice1234",
        "display_name": "Alice Chen",
        "bio": "Food blogger and home baker. I share simple recipes that actually work.",
    },
    {
        "username": "benchef",
        "email": "ben@plateful.com",
        "password": "ben1234",
        "display_name": "Ben Nguyen",
        "bio": "Weeknight cook. Mostly Asian-inspired, always quick.",
    },
    {
        "username": "carakitchen",
        "email": "cara@plateful.com",
        "password": "cara1234",
        "display_name": "Cara Rossi",
        "bio": "Trained in Florence. Now cooking for fun and sharing everything I know.",
    },
]

RECIPES = [
    {
        "author": "carakitchen",
        "title": "Spaghetti Carbonara",
        "cuisine": "Italian",
        "difficulty": "Easy",
        "prep_time": 20,
        "servings": 2,
        "meal_type": "Dinner",
        "description": "A classic Roman pasta — creamy without any cream. Just eggs, Pecorino, guanciale and pasta water.",
        "ingredients": [
            "200g spaghetti",
            "100g guanciale or pancetta",
            "2 large eggs",
            "50g Pecorino Romano, finely grated",
            "50g Parmesan, finely grated",
            "Black pepper",
            "Salt",
        ],
        "steps": [
            "Bring a large pot of salted water to the boil and cook spaghetti until al dente.",
            "While pasta cooks, fry guanciale in a cold pan over medium heat until crispy. Remove from heat.",
            "Whisk eggs with Pecorino, Parmesan, and a generous amount of black pepper in a bowl.",
            "Reserve a cup of pasta water before draining.",
            "Add hot pasta to the guanciale pan off the heat. Pour egg mixture over and toss quickly, adding pasta water a splash at a time until silky.",
            "Serve immediately with extra cheese and black pepper.",
        ],
    },
    {
        "author": "alicecooks",
        "title": "Chicken Tikka Masala",
        "cuisine": "Indian",
        "difficulty": "Medium",
        "prep_time": 45,
        "servings": 4,
        "meal_type": "Dinner",
        "description": "Tender marinated chicken in a rich, spiced tomato cream sauce. Great with naan or basmati rice.",
        "ingredients": [
            "700g chicken breast, cubed",
            "150g plain yoghurt",
            "2 tbsp tikka masala paste",
            "1 onion, diced",
            "3 garlic cloves, minced",
            "1 tsp grated ginger",
            "400g tin crushed tomatoes",
            "150ml double cream",
            "1 tsp garam masala",
            "Salt and oil",
        ],
        "steps": [
            "Marinate chicken in yoghurt and tikka paste for at least 30 minutes.",
            "Grill or pan-fry chicken until charred at the edges. Set aside.",
            "Fry onion in oil until golden. Add garlic and ginger, cook 1 minute.",
            "Stir in crushed tomatoes and simmer 10 minutes.",
            "Add cream and garam masala. Return chicken to the pan.",
            "Simmer 10 minutes, season to taste, and serve.",
        ],
    },
    {
        "author": "benchef",
        "title": "Avocado Toast",
        "cuisine": "American",
        "difficulty": "Easy",
        "prep_time": 10,
        "servings": 1,
        "meal_type": "Breakfast",
        "description": "The classic done properly — creamy avocado, good bread, and the right toppings.",
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "Juice of half a lemon",
            "Chilli flakes",
            "Flaky sea salt",
            "2 eggs (optional, poached)",
        ],
        "steps": [
            "Toast bread until golden and crisp.",
            "Halve avocado, remove stone, and scoop flesh into a bowl.",
            "Mash with lemon juice and a pinch of salt.",
            "Spread avocado on toast. Top with chilli flakes and flaky salt.",
            "Add poached eggs on top if using, and serve immediately.",
        ],
    },
    {
        "author": "carakitchen",
        "title": "Pad Thai",
        "cuisine": "Thai",
        "difficulty": "Medium",
        "prep_time": 30,
        "servings": 2,
        "meal_type": "Dinner",
        "description": "Street-food style Pad Thai with the proper tangy-sweet-salty balance.",
        "ingredients": [
            "200g flat rice noodles",
            "200g prawns or tofu",
            "2 eggs",
            "3 tbsp fish sauce",
            "2 tbsp tamarind paste",
            "1 tbsp palm sugar",
            "3 spring onions, sliced",
            "Bean sprouts",
            "Crushed peanuts",
            "Lime wedges",
            "Vegetable oil",
        ],
        "steps": [
            "Soak noodles in warm water for 20 minutes until pliable. Drain.",
            "Mix fish sauce, tamarind paste, and palm sugar into a sauce.",
            "Heat wok over high heat. Stir-fry prawns or tofu until cooked. Push to one side.",
            "Crack in eggs and scramble briefly, then mix with protein.",
            "Add noodles and sauce. Toss constantly for 2–3 minutes.",
            "Remove from heat, toss with spring onions and bean sprouts.",
            "Serve topped with peanuts and a lime wedge.",
        ],
    },
    {
        "author": "alicecooks",
        "title": "Banana Pancakes",
        "cuisine": "American",
        "difficulty": "Easy",
        "prep_time": 20,
        "servings": 2,
        "meal_type": "Breakfast",
        "description": "Fluffy pancakes with ripe banana folded right into the batter. No syrup needed.",
        "ingredients": [
            "2 ripe bananas",
            "2 eggs",
            "100g plain flour",
            "1 tsp baking powder",
            "120ml milk",
            "Pinch of salt",
            "Butter for frying",
        ],
        "steps": [
            "Mash bananas in a bowl until smooth.",
            "Whisk in eggs and milk.",
            "Fold in flour, baking powder, and salt until just combined — lumps are fine.",
            "Melt a small knob of butter in a non-stick pan over medium heat.",
            "Pour in batter to form small rounds. Cook until bubbles form, then flip.",
            "Cook 1 more minute and serve warm.",
        ],
    },
    {
        "author": "benchef",
        "title": "Greek Salad",
        "cuisine": "Mediterranean",
        "difficulty": "Easy",
        "prep_time": 15,
        "servings": 2,
        "meal_type": "Lunch",
        "description": "The real thing — chunky vegetables, good olives, feta on top. No lettuce.",
        "ingredients": [
            "3 tomatoes, cut into wedges",
            "1 cucumber, roughly chopped",
            "1 red onion, thinly sliced",
            "150g Kalamata olives",
            "150g feta cheese",
            "3 tbsp extra virgin olive oil",
            "1 tsp dried oregano",
            "Salt and pepper",
        ],
        "steps": [
            "Combine tomatoes, cucumber, and red onion in a bowl.",
            "Scatter olives over the top.",
            "Place feta as a whole slab on top (don't crumble it).",
            "Drizzle with olive oil, sprinkle oregano, season with salt and pepper.",
            "Serve with crusty bread.",
        ],
    },
    {
        "author": "demo",
        "title": "Butter Chicken",
        "cuisine": "Indian",
        "difficulty": "Medium",
        "prep_time": 50,
        "servings": 4,
        "meal_type": "Dinner",
        "description": "Mildly spiced, velvety tomato-butter sauce with tender chicken. Perfect with naan.",
        "ingredients": [
            "700g chicken thighs, cubed",
            "150g plain yoghurt",
            "2 tsp garam masala",
            "1 tsp turmeric",
            "1 onion, diced",
            "3 garlic cloves",
            "1 tsp grated ginger",
            "400g tin crushed tomatoes",
            "100ml double cream",
            "50g butter",
            "Salt",
        ],
        "steps": [
            "Marinate chicken in yoghurt, 1 tsp garam masala, and turmeric for 30 minutes.",
            "Grill or pan-fry chicken until cooked through. Set aside.",
            "Melt butter in a pan. Fry onion until golden, then add garlic and ginger.",
            "Add tomatoes and simmer 15 minutes until thickened.",
            "Blend sauce until smooth, then return to pan.",
            "Stir in cream and remaining garam masala. Add chicken and simmer 10 minutes.",
            "Season and serve with naan or rice.",
        ],
    },
    {
        "author": "carakitchen",
        "title": "Miso Soup",
        "cuisine": "Japanese",
        "difficulty": "Easy",
        "prep_time": 15,
        "servings": 2,
        "meal_type": "Breakfast",
        "description": "Light, warming miso broth with tofu and wakame. Done in 15 minutes.",
        "ingredients": [
            "600ml dashi stock (or water)",
            "2 tbsp white miso paste",
            "100g silken tofu, cubed",
            "1 tbsp dried wakame seaweed",
            "2 spring onions, sliced",
        ],
        "steps": [
            "Bring dashi to a gentle simmer — do not boil.",
            "Soak wakame in cold water for 5 minutes, then drain.",
            "Whisk miso paste into a ladleful of hot dashi, then stir back into the pot.",
            "Add tofu and wakame. Heat through for 2 minutes without boiling.",
            "Serve topped with spring onions.",
        ],
    },
]

SAVES = [
    ("demo", "Spaghetti Carbonara"),
    ("demo", "Chicken Tikka Masala"),
    ("demo", "Pad Thai"),
    ("demo", "Banana Pancakes"),
    ("alicecooks", "Spaghetti Carbonara"),
    ("alicecooks", "Pad Thai"),
    ("benchef", "Butter Chicken"),
    ("carakitchen", "Greek Salad"),
]

FOLLOWS = [
    ("demo", "alicecooks"),
    ("demo", "benchef"),
    ("demo", "carakitchen"),
    ("alicecooks", "carakitchen"),
    ("benchef", "alicecooks"),
]


def seed():
    with app.app_context():
        print("Clearing existing data...")
        Activity.query.delete()
        Follow.query.delete()
        SavedRecipe.query.delete()
        RecipeStep.query.delete()
        Ingredient.query.delete()
        Recipe.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        user_map = {}
        for data in USERS:
            u = User(
                username=data["username"],
                email=data["email"],
                display_name=data["display_name"],
                bio=data["bio"],
            )
            u.set_password(data["password"])
            db.session.add(u)
            user_map[data["username"]] = u
        db.session.commit()

        print("Creating recipes...")
        recipe_map = {}
        for data in RECIPES:
            author = user_map[data["author"]]
            r = Recipe(
                author_id=author.id,
                title=data["title"],
                cuisine=data["cuisine"],
                difficulty=data["difficulty"],
                prep_time=data["prep_time"],
                servings=data["servings"],
                meal_type=data["meal_type"],
                description=data["description"],
            )
            db.session.add(r)
            db.session.flush()

            for name in data["ingredients"]:
                db.session.add(Ingredient(recipe_id=r.id, name=name))

            for i, instruction in enumerate(data["steps"], start=1):
                db.session.add(RecipeStep(recipe_id=r.id, step_number=i, instruction=instruction))

            db.session.add(Activity(
                user_id=author.id,
                activity_type="uploaded_recipe",
                related_recipe_id=r.id,
            ))

            recipe_map[data["title"]] = r

        db.session.commit()

        print("Creating follows...")
        for follower_username, following_username in FOLLOWS:
            db.session.add(Follow(
                follower_id=user_map[follower_username].id,
                following_id=user_map[following_username].id,
            ))
        db.session.commit()

        print("Creating saved recipes...")
        for username, recipe_title in SAVES:
            user = user_map[username]
            recipe = recipe_map[recipe_title]
            db.session.add(SavedRecipe(user_id=user.id, recipe_id=recipe.id))
            db.session.add(Activity(
                user_id=user.id,
                activity_type="saved_recipe",
                related_recipe_id=recipe.id,
            ))
        db.session.commit()

        print("Done! Seed data created.")
        print("\nDemo login: demo@plateful.com / demo1234")
        print("Other accounts:")
        for u in USERS[1:]:
            print(f"  {u['email']} / {u['password']}")


if __name__ == "__main__":
    seed()
