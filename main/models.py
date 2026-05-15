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
    ingredients = db.relationship("Ingredient", backref="recipe", lazy=True, cascade="all, delete-orphan")
    steps = db.relationship("RecipeStep", backref="recipe", lazy=True, cascade="all, delete-orphan")
    saved_by = db.relationship("SavedRecipe", backref="recipe", lazy=True, cascade="all, delete-orphan")
    meal_plan_entries = db.relationship("MealPlanEntry", backref="recipe", lazy=True, cascade="all, delete-orphan")
    
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


def create_test_data():
    from main import db

    _USERS = [
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

    _RECIPES = [
        {
            "author": "carakitchen",
            "title": "Spaghetti Carbonara",
            "cuisine": "Italian",
            "difficulty": "Easy",
            "prep_time": 20,
            "servings": 2,
            "meal_type": "Dinner",
            "image_url": "uploads/spaghetti.jpg",
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
            "image_url": "uploads/chickentikkamasala.webp",
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
            "image_url": "uploads/avocadotoast.jpg",
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
            "image_url": "uploads/pad_thai.jpg",
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
            "image_url": "uploads/banana_pancakes.jpg",
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
            "image_url": "uploads/greeksalad.png",
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
            "image_url": "uploads/butterchicken.jpg",
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
            "image_url": "uploads/misosoup.jpg",
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
        {
            "author": "alicecooks",
            "title": "Garlic Fried Rice",
            "cuisine": "Chinese",
            "difficulty": "Easy",
            "prep_time": 15,
            "servings": 2,
            "meal_type": "Lunch",
            "image_url": "uploads/garlicfriedrice.jpg",
            "description": "The best use of leftover rice — fragrant, savoury, and ready in minutes.",
            "ingredients": [
                "2 cups cooked jasmine rice (day-old)",
                "4 garlic cloves, minced",
                "2 eggs",
                "2 tbsp soy sauce",
                "1 tsp sesame oil",
                "2 spring onions, sliced",
                "Vegetable oil",
            ],
            "steps": [
                "Heat a wok over high heat with a splash of oil.",
                "Fry garlic for 30 seconds until fragrant.",
                "Push garlic to the side, crack in eggs and scramble.",
                "Add rice and break up any clumps. Stir-fry 3 minutes.",
                "Add soy sauce and toss to coat evenly.",
                "Remove from heat, drizzle with sesame oil, top with spring onions.",
            ],
        },
        {
            "author": "benchef",
            "title": "Shakshuka",
            "cuisine": "Mediterranean",
            "difficulty": "Easy",
            "prep_time": 25,
            "servings": 2,
            "meal_type": "Breakfast",
            "image_url": "uploads/shakshuka.jpg",
            "description": "Eggs poached in a spiced tomato and pepper sauce. Great with crusty bread.",
            "ingredients": [
                "400g tin crushed tomatoes",
                "1 red pepper, diced",
                "1 onion, diced",
                "3 garlic cloves, minced",
                "1 tsp cumin",
                "1 tsp paprika",
                "Pinch of chilli flakes",
                "4 eggs",
                "Fresh parsley",
                "Olive oil",
            ],
            "steps": [
                "Heat olive oil in a wide pan. Fry onion and pepper until soft.",
                "Add garlic, cumin, paprika, and chilli. Cook 1 minute.",
                "Pour in tomatoes and simmer 10 minutes until sauce thickens.",
                "Make wells in the sauce and crack in eggs.",
                "Cover and cook 5–7 minutes until whites are set but yolks still runny.",
                "Scatter parsley and serve straight from the pan.",
            ],
        },
        {
            "author": "demo",
            "title": "Beef Tacos",
            "cuisine": "Mexican",
            "difficulty": "Easy",
            "prep_time": 20,
            "servings": 4,
            "meal_type": "Breakfast",
            "image_url": "uploads/beeftacos.jpg",
            "description": "Quick weeknight tacos with well-seasoned beef, fresh toppings, and warm tortillas.",
            "ingredients": [
                "500g beef mince",
                "8 small corn or flour tortillas",
                "1 tsp cumin",
                "1 tsp smoked paprika",
                "1/2 tsp garlic powder",
                "Salt and pepper",
                "1 cup shredded lettuce",
                "2 tomatoes, diced",
                "Sour cream",
                "Grated cheddar",
                "Lime wedges",
            ],
            "steps": [
                "Cook mince in a hot pan, breaking it up, until browned.",
                "Add cumin, paprika, garlic powder, salt and pepper. Stir well.",
                "Add a splash of water and simmer 3 minutes.",
                "Warm tortillas in a dry pan or microwave.",
                "Fill tortillas with beef, lettuce, tomato, cheese, and sour cream.",
                "Serve with lime wedges.",
            ],
        },
        {
            "author": "carakitchen",
            "title": "Lemon Pasta",
            "cuisine": "Italian",
            "difficulty": "Easy",
            "prep_time": 15,
            "servings": 2,
            "meal_type": "Lunch",
            "image_url": "uploads/lemonpasta.jpg",
            "description": "Bright, buttery pasta with lemon zest and Parmesan. On the table in 15 minutes.",
            "ingredients": [
                "200g spaghetti or linguine",
                "Zest and juice of 1 lemon",
                "40g butter",
                "50g Parmesan, grated",
                "2 tbsp olive oil",
                "Salt and black pepper",
                "Fresh basil or parsley",
            ],
            "steps": [
                "Cook pasta in well-salted water until al dente. Reserve 1 cup pasta water.",
                "Melt butter with olive oil in a pan over low heat.",
                "Add lemon zest and juice, stir briefly.",
                "Add drained pasta and toss, adding pasta water to loosen.",
                "Remove from heat, stir in Parmesan.",
                "Season generously and top with fresh herbs.",
            ],
        },
        {
            "author": "benchef",
            "title": "Teriyaki Salmon",
            "cuisine": "Japanese",
            "difficulty": "Easy",
            "prep_time": 20,
            "servings": 2,
            "meal_type": "Dinner",
            "image_url": "uploads/teriyakisalmon.webp",
            "description": "Glossy teriyaki-glazed salmon fillets, ready in under 20 minutes.",
            "ingredients": [
                "2 salmon fillets",
                "3 tbsp soy sauce",
                "2 tbsp mirin",
                "1 tbsp sake or dry sherry",
                "1 tsp sugar",
                "Sesame seeds",
                "Spring onions",
                "Steamed rice to serve",
            ],
            "steps": [
                "Mix soy sauce, mirin, sake, and sugar into a sauce.",
                "Heat oil in a pan over medium-high heat.",
                "Cook salmon skin-side down for 3 minutes until crispy.",
                "Flip and cook 2 more minutes.",
                "Pour sauce over salmon and let it bubble and glaze for 1 minute.",
                "Serve over rice, topped with sesame seeds and spring onions.",
            ],
        },
    ]

    _SAVES = [
        ("demo", "Spaghetti Carbonara"),
        ("demo", "Chicken Tikka Masala"),
        ("demo", "Pad Thai"),
        ("demo", "Banana Pancakes"),
        ("alicecooks", "Spaghetti Carbonara"),
        ("alicecooks", "Pad Thai"),
        ("benchef", "Butter Chicken"),
        ("carakitchen", "Greek Salad"),
    ]

    _FOLLOWS = [
        ("demo", "alicecooks"),
        ("demo", "benchef"),
        ("demo", "carakitchen"),
        ("alicecooks", "carakitchen"),
        ("benchef", "alicecooks"),
    ]

    # Clear existing data
    Activity.query.delete()
    Follow.query.delete()
    SavedRecipe.query.delete()
    RecipeStep.query.delete()
    Ingredient.query.delete()
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    # Create users
    user_map = {}
    for data in _USERS:
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

    # Create recipes with ingredients, steps, and activity
    recipe_map = {}
    for data in _RECIPES:
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
            image_url=data.get("image_url"),
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

    # Create follows
    for follower_username, following_username in _FOLLOWS:
        db.session.add(Follow(
            follower_id=user_map[follower_username].id,
            following_id=user_map[following_username].id,
        ))
    db.session.commit()

    # Create saved recipes and activity
    for username, recipe_title in _SAVES:
        user = user_map[username]
        recipe = recipe_map[recipe_title]
        db.session.add(SavedRecipe(user_id=user.id, recipe_id=recipe.id))
        db.session.add(Activity(
            user_id=user.id,
            activity_type="saved_recipe",
            related_recipe_id=recipe.id,
        ))
    db.session.commit()

    print("Test data created successfully.")
    print("Demo login: demo@plateful.com / demo1234")
