import unittest
from sqlalchemy.exc import IntegrityError
from main import create_app, db
from main.config import TestConfig
from main.models import User, Recipe, Ingredient, RecipeStep, SavedRecipe, Follow


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


if __name__ == '__main__':
    unittest.main()