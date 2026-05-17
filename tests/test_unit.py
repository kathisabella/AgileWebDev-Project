import unittest
from datetime import date
from sqlalchemy.exc import IntegrityError
from main import create_app, db
from main.config import TestConfig
from main.models import User, Recipe, Ingredient, RecipeStep, SavedRecipe, Follow, MealPlanEntry, Activity


def add_test_data():
    user1 = User(username='testchef', email='testchef@plateful.com', display_name='Test Chef')
    user1.set_password('correctpassword')

    user2 = User(username='foodlover', email='foodlover@plateful.com', display_name='Food Lover')
    user2.set_password('password123')

    db.session.add_all([user1, user2])
    db.session.commit()

    recipe = Recipe(
        author_id=user1.id,
        title='Test Pasta',
        cuisine='Italian',
        difficulty='Easy',
        prep_time=20,
        servings=2,
        meal_type='Dinner',
        description='A test recipe'
    )
    db.session.add(recipe)
    db.session.commit()

    db.session.add(Ingredient(recipe_id=recipe.id, name='Pasta'))
    db.session.add(RecipeStep(recipe_id=recipe.id, step_number=1, instruction='Boil pasta'))
    db.session.commit()


class UserModelTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Password tests ---

    def test_password_correct(self):
        u = User.query.filter_by(username='testchef').first()
        self.assertTrue(u.check_password('correctpassword'),
                        'check_password should return True for the correct password')

    def test_password_wrong(self):
        u = User.query.filter_by(username='testchef').first()
        self.assertFalse(u.check_password('wrongpassword'),
                         'check_password should return False for an incorrect password')

    def test_password_not_stored_as_plaintext(self):
        u = User.query.filter_by(username='testchef').first()
        self.assertNotEqual(u.password_hash, 'correctpassword',
                            'Password should be hashed, not stored as plain text')

    # --- User tests ---

    def test_user_created_in_db(self):
        u = User.query.filter_by(username='testchef').first()
        self.assertIsNotNone(u, 'User testchef should exist in the database')

    def test_duplicate_username_rejected(self):
        duplicate = User(username='testchef', email='other@plateful.com', display_name='Other')
        duplicate.set_password('somepassword')
        db.session.add(duplicate)
        with self.assertRaises(IntegrityError,
                               msg='Duplicate username should raise an IntegrityError'):
            db.session.commit()

    def test_duplicate_email_rejected(self):
        duplicate = User(username='newuser', email='testchef@plateful.com', display_name='New')
        duplicate.set_password('somepassword')
        db.session.add(duplicate)
        with self.assertRaises(IntegrityError,
                               msg='Duplicate email should raise an IntegrityError'):
            db.session.commit()

    def test_user_joined_date_set_automatically(self):
        u = User.query.filter_by(username='testchef').first()
        self.assertIsNotNone(u.joined_date,
                             'joined_date should be set automatically on user creation')

    # --- Recipe tests ---

    def test_recipe_linked_to_author(self):
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        self.assertIsNotNone(recipe, 'Test Pasta recipe should exist in the database')
        self.assertEqual(recipe.author.username, 'testchef',
                         'Recipe author should be testchef')

    def test_recipe_count_for_user(self):
        user = User.query.filter_by(username='testchef').first()
        count = Recipe.query.filter_by(author_id=user.id).count()
        self.assertEqual(count, 1, 'testchef should have exactly 1 recipe')

    def test_recipe_has_ingredient(self):
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        self.assertEqual(len(recipe.ingredients), 1,
                         'Test Pasta should have exactly 1 ingredient')
        self.assertEqual(recipe.ingredients[0].name, 'Pasta',
                         'Ingredient name should be Pasta')

    def test_recipe_has_step(self):
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        self.assertEqual(len(recipe.steps), 1,
                         'Test Pasta should have exactly 1 step')
        self.assertEqual(recipe.steps[0].instruction, 'Boil pasta',
                         'Step instruction should be Boil pasta')

    def test_recipe_fields_stored_correctly(self):
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        self.assertEqual(recipe.cuisine, 'Italian', 'Cuisine should be Italian')
        self.assertEqual(recipe.difficulty, 'Easy', 'Difficulty should be Easy')
        self.assertEqual(recipe.prep_time, 20, 'Prep time should be 20')
        self.assertEqual(recipe.servings, 2, 'Servings should be 2')
        self.assertEqual(recipe.meal_type, 'Dinner', 'Meal type should be Dinner')

    # --- Save recipe tests ---

    def test_save_recipe(self):
        user = User.query.filter_by(username='foodlover').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        db.session.add(SavedRecipe(user_id=user.id, recipe_id=recipe.id))
        db.session.commit()
        result = SavedRecipe.query.filter_by(user_id=user.id, recipe_id=recipe.id).first()
        self.assertIsNotNone(result, 'Recipe should appear in saved recipes after saving')

    def test_duplicate_save_rejected(self):
        user = User.query.filter_by(username='foodlover').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        db.session.add(SavedRecipe(user_id=user.id, recipe_id=recipe.id))
        db.session.commit()
        db.session.add(SavedRecipe(user_id=user.id, recipe_id=recipe.id))
        with self.assertRaises(IntegrityError,
                               msg='Saving the same recipe twice should raise an IntegrityError'):
            db.session.commit()

    def test_unsave_recipe(self):
        user = User.query.filter_by(username='foodlover').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        saved = SavedRecipe(user_id=user.id, recipe_id=recipe.id)
        db.session.add(saved)
        db.session.commit()
        db.session.delete(saved)
        db.session.commit()
        result = SavedRecipe.query.filter_by(user_id=user.id, recipe_id=recipe.id).first()
        self.assertIsNone(result, 'Recipe should be removed from saved recipes after unsaving')

    # --- Follow tests ---

    def test_follow_user(self):
        user1 = User.query.filter_by(username='testchef').first()
        user2 = User.query.filter_by(username='foodlover').first()
        db.session.add(Follow(follower_id=user2.id, following_id=user1.id))
        db.session.commit()
        result = Follow.query.filter_by(follower_id=user2.id, following_id=user1.id).first()
        self.assertIsNotNone(result, 'Follow relationship should exist after following a user')

    def test_unfollow_user(self):
        user1 = User.query.filter_by(username='testchef').first()
        user2 = User.query.filter_by(username='foodlover').first()
        follow = Follow(follower_id=user2.id, following_id=user1.id)
        db.session.add(follow)
        db.session.commit()
        db.session.delete(follow)
        db.session.commit()
        result = Follow.query.filter_by(follower_id=user2.id, following_id=user1.id).first()
        self.assertIsNone(result, 'Follow relationship should be gone after unfollowing')

    def test_cannot_follow_yourself(self):
        user = User.query.filter_by(username='testchef').first()
        follow = Follow.query.filter_by(follower_id=user.id, following_id=user.id).first()
        self.assertIsNone(follow,
                          'A user should not be able to follow themselves')

    def test_duplicate_follow_rejected(self):
        user1 = User.query.filter_by(username='testchef').first()
        user2 = User.query.filter_by(username='foodlover').first()
        db.session.add(Follow(follower_id=user2.id, following_id=user1.id))
        db.session.commit()
        db.session.add(Follow(follower_id=user2.id, following_id=user1.id))
        with self.assertRaises(IntegrityError,
                               msg='Following the same user twice should raise an IntegrityError'):
            db.session.commit()

    # --- MealPlanEntry tests ---

    def test_meal_plan_entry_saved(self):
        user = User.query.filter_by(username='testchef').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        entry = MealPlanEntry(
            user_id=user.id,
            recipe_id=recipe.id,
            day='Day 1',
            meal_type='Dinner',
            week_start_date=date.today()
        )
        db.session.add(entry)
        db.session.commit()
        result = MealPlanEntry.query.filter_by(user_id=user.id, day='Day 1', meal_type='Dinner').first()
        self.assertIsNotNone(result, 'MealPlanEntry should exist after being saved')
        self.assertEqual(result.recipe_id, recipe.id,
                         'MealPlanEntry should reference the correct recipe')

    def test_meal_plan_entry_without_recipe(self):
        user = User.query.filter_by(username='testchef').first()
        entry = MealPlanEntry(
            user_id=user.id,
            recipe_id=None,
            day='Day 2',
            meal_type='Breakfast',
            week_start_date=date.today()
        )
        db.session.add(entry)
        db.session.commit()
        result = MealPlanEntry.query.filter_by(user_id=user.id, day='Day 2').first()
        self.assertIsNotNone(result, 'MealPlanEntry with no recipe should still be saved')
        self.assertIsNone(result.recipe_id, 'recipe_id should be None for an empty slot')

    # --- Activity tests ---

    def test_activity_recorded_for_upload(self):
        user = User.query.filter_by(username='testchef').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        db.session.add(Activity(
            user_id=user.id,
            activity_type='uploaded_recipe',
            related_recipe_id=recipe.id
        ))
        db.session.commit()
        result = Activity.query.filter_by(user_id=user.id, activity_type='uploaded_recipe').first()
        self.assertIsNotNone(result, 'Activity record should exist after uploading a recipe')
        self.assertEqual(result.related_recipe_id, recipe.id,
                         'Activity should reference the correct recipe')

    def test_activity_recorded_for_follow(self):
        user1 = User.query.filter_by(username='testchef').first()
        user2 = User.query.filter_by(username='foodlover').first()
        db.session.add(Activity(
            user_id=user2.id,
            activity_type='followed_user',
            related_user_id=user1.id
        ))
        db.session.commit()
        result = Activity.query.filter_by(user_id=user2.id, activity_type='followed_user').first()
        self.assertIsNotNone(result, 'Activity record should exist after following a user')
        self.assertEqual(result.related_user_id, user1.id,
                         'Activity should reference the correct followed user')

    def test_activity_recorded_for_save(self):
        user = User.query.filter_by(username='foodlover').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        db.session.add(Activity(
            user_id=user.id,
            activity_type='saved_recipe',
            related_recipe_id=recipe.id
        ))
        db.session.commit()
        result = Activity.query.filter_by(user_id=user.id, activity_type='saved_recipe').first()
        self.assertIsNotNone(result, 'Activity record should exist after saving a recipe')
        self.assertEqual(result.related_recipe_id, recipe.id,
                         'Activity should reference the correct saved recipe')

    def test_multiple_activities_for_user(self):
        user = User.query.filter_by(username='testchef').first()
        recipe = Recipe.query.filter_by(title='Test Pasta').first()
        db.session.add(Activity(user_id=user.id, activity_type='uploaded_recipe', related_recipe_id=recipe.id))
        db.session.add(Activity(user_id=user.id, activity_type='saved_recipe', related_recipe_id=recipe.id))
        db.session.commit()
        count = Activity.query.filter_by(user_id=user.id).count()
        self.assertEqual(count, 2, 'User should have 2 activity records')


if __name__ == '__main__':
    unittest.main()