import unittest
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from main import create_app, db
from main.config import SeleniumTestConfig
from main.models import User, Recipe

BASE_URL = 'http://localhost:5001'


def add_test_data():
    user1 = User(username='seleniumchef', email='selenium@plateful.com', display_name='Selenium Chef')
    user1.set_password('testpassword')
    db.session.add(user1)
    db.session.commit()

    user2 = User(username='seleniumfan', email='fan@plateful.com', display_name='Selenium Fan')
    user2.set_password('fanpassword')
    db.session.add(user2)
    db.session.commit()

    recipe = Recipe(
        author_id=user1.id,
        title='Selenium Pasta',
        cuisine='Italian',
        difficulty='Easy',
        prep_time=20,
        servings=2,
        meal_type='Dinner',
        description='A selenium test recipe'
    )
    db.session.add(recipe)
    db.session.commit()


class SystemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Start Flask server once for all tests."""
        cls.app = create_app(SeleniumTestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        add_test_data()

        cls.server_thread = threading.Thread(
            target=lambda: cls.app.run(port=5001, use_reloader=False)
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Drop DB and clean up after all tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        if os.path.exists('selenium_test.db'):
            os.remove('selenium_test.db')

    def setUp(self):
        """Fresh browser (no cookies) for each test."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.quit()

    # --- Helper ---

    def login(self, email='selenium@plateful.com', password='testpassword'):
        self.driver.get(f'{BASE_URL}/')
        self.driver.find_element(By.NAME, 'email').send_keys(email)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, '#panel-login button[type=submit]').click()
        WebDriverWait(self.driver, 10).until(EC.url_changes(f'{BASE_URL}/'))

    # --- Authentication tests ---

    def test_login_page_loads(self):
        self.driver.get(f'{BASE_URL}/')
        self.assertIn('Plateful', self.driver.title,
                      'Login page title should contain Plateful')

    def test_valid_login_redirects_to_dashboard(self):
        self.login()
        self.assertIn('/dashboard', self.driver.current_url,
                      'Valid login should redirect to dashboard')

    def test_invalid_login_shows_error(self):
        self.driver.get(f'{BASE_URL}/')
        self.driver.find_element(By.NAME, 'email').send_keys('selenium@plateful.com')
        self.driver.find_element(By.NAME, 'password').send_keys('wrongpassword')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-login button[type=submit]').click()
        error = self.driver.find_element(By.CLASS_NAME, 'form-error')
        self.assertIsNotNone(error,
                             'Invalid login should display an error message')

    def test_logout_redirects_to_login(self):
        self.login()
        logout_form = self.driver.find_element(By.CSS_SELECTOR, 'form[action*="logout"]')
        logout_form.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        WebDriverWait(self.driver, 10).until(EC.url_to_be(f'{BASE_URL}/'))
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Logout should redirect to the login page')

    def test_signup_creates_account_and_redirects(self):
        self.driver.get(f'{BASE_URL}/')
        signup_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="signup"]')
        self.driver.execute_script("arguments[0].click();", signup_tab)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#panel-signup input[name="first_name"]'))
        )
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="first_name"]').send_keys('Test')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="last_name"]').send_keys('User')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="username"]').send_keys('newseleniumuser')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="email"]').send_keys('newuser@plateful.com')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="password"]').send_keys('securepassword')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup input[name="accept_terms"]').click()
        self.driver.find_element(By.CSS_SELECTOR, '#panel-signup button[type=submit]').click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/dashboard'))
        self.assertIn('/dashboard', self.driver.current_url,
                      'Successful signup should redirect to dashboard')

    # --- Page access / auth guard tests ---

    def test_explore_requires_login(self):
        self.driver.get(f'{BASE_URL}/explore')
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Unauthenticated access to /explore should redirect to login page')

    def test_dashboard_requires_login(self):
        self.driver.get(f'{BASE_URL}/dashboard')
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Unauthenticated access to /dashboard should redirect to login page')

    def test_profile_requires_login(self):
        self.driver.get(f'{BASE_URL}/profile')
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Unauthenticated access to /profile should redirect to login page')

    def test_saved_recipes_requires_login(self):
        self.driver.get(f'{BASE_URL}/saved')
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Unauthenticated access to /saved should redirect to login page')

    # --- Explore tests ---

    def test_explore_shows_recipes_after_login(self):
        self.login()
        self.driver.get(f'{BASE_URL}/explore')
        cards = self.driver.find_elements(By.CLASS_NAME, 'recipe-card')
        self.assertGreater(len(cards), 0,
                           'Explore page should show at least one recipe card after login')

    def test_explore_recipe_links_to_details(self):
        self.login()
        self.driver.get(f'{BASE_URL}/explore')
        view_btn = self.driver.find_element(By.CSS_SELECTOR, '.recipe-card .btn')
        view_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/recipe/'))
        self.assertIn('/recipe/', self.driver.current_url,
                      'Clicking View on a recipe card should navigate to recipe details')

    # --- My Recipes tests ---

    def test_my_recipes_page_loads(self):
        self.login()
        self.driver.get(f'{BASE_URL}/my-recipes')
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Pasta', body,
                      'My Recipes page should display recipes created by the logged-in user')

    # --- Dashboard tests ---

    def test_dashboard_loads_with_content(self):
        self.login()
        self.assertIn('/dashboard', self.driver.current_url,
                      'Should be on dashboard after login')
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Chef', body,
                      'Dashboard should display the logged-in user display name')

    # --- Recipe details tests ---

    def test_recipe_details_page_loads(self):
        self.login()
        self.driver.get(f'{BASE_URL}/explore')
        view_btn = self.driver.find_element(By.CSS_SELECTOR, '.recipe-card .btn')
        view_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/recipe/'))
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Pasta', body,
                      'Recipe details page should display the recipe title')

    def test_recipe_details_shows_author(self):
        self.login()
        self.driver.get(f'{BASE_URL}/explore')
        view_btn = self.driver.find_element(By.CSS_SELECTOR, '.recipe-card .btn')
        view_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/recipe/'))
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Chef', body,
                      'Recipe details page should display the author name')

    # --- Save / saved tests ---

    def test_save_recipe(self):
        # Login as seleniumfan — Save button is hidden for the recipe's own author
        self.login(email='fan@plateful.com', password='fanpassword')
        self.driver.get(f'{BASE_URL}/explore')
        view_btn = self.driver.find_element(By.CSS_SELECTOR, '.recipe-card .btn')
        view_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/recipe/'))
        save_btn = self.driver.find_element(By.CSS_SELECTOR, 'form[action$="/save"] button[type=submit]')
        save_btn.click()
        # Wait for page reload — unsave form only appears after save completes
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'form[action$="/unsave"]'))
        )
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Saved', body,
                      'Recipe page should show saved status after clicking Save')

    def test_saved_recipes_page_shows_saved_recipe(self):
        # Login as seleniumfan — Save button is hidden for the recipe's own author
        self.login(email='fan@plateful.com', password='fanpassword')
        self.driver.get(f'{BASE_URL}/explore')
        view_btn = self.driver.find_element(By.CSS_SELECTOR, '.recipe-card .btn')
        view_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/recipe/'))
        save_btn = self.driver.find_element(By.CSS_SELECTOR, 'form[action$="/save"] button[type=submit]')
        save_btn.click()
        # Wait for page reload — unsave form only appears after save completes
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'form[action$="/unsave"]'))
        )
        self.driver.get(f'{BASE_URL}/saved')
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Pasta', body,
                      'Saved recipes page should display the recipe that was just saved')

    # --- Social / following tests ---

    def test_following_page_loads(self):
        self.login()
        self.driver.get(f'{BASE_URL}/following')
        self.assertIn('/following', self.driver.current_url,
                      'Following page should load for logged-in user')

    def test_following_page_has_suggested_section(self):
        self.login()
        self.driver.get(f'{BASE_URL}/following')
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Suggested accounts', body,
                      'Following page should display the Suggested accounts section')

    def test_follow_user_from_following_page(self):
        self.login()
        self.driver.get(f'{BASE_URL}/following')
        follow_btn = self.driver.find_element(By.CSS_SELECTOR, 'form[action*="/follow/"] button[type=submit]')
        follow_btn.click()
        WebDriverWait(self.driver, 10).until(EC.url_contains('/following'))
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Fan', body,
                      'Followed user should appear on the Following page after being followed')

    # --- Profile tests ---

    def test_profile_page_shows_display_name(self):
        self.login()
        self.driver.get(f'{BASE_URL}/profile')
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Selenium Chef', body,
                      'Profile page should display the logged-in user display name')


if __name__ == '__main__':
    unittest.main()