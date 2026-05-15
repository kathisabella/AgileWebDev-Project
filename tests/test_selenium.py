import unittest
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from main import create_app, db
from main.config import SeleniumTestConfig
from main.models import User, Recipe

BASE_URL = 'http://localhost:5001'

def add_test_data():
    user = User(username='seleniumchef', email='selenium@plateful.com', display_name='Selenium Chef')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()

    recipe = Recipe(
        author_id=user.id,
        title='Selenium Pasta',
        cuisine='Italian',
        difficulty='Easy',
        prep_time=20,
        servings=2,
        description='A selenium test recipe'
    )
    db.session.add(recipe)
    db.session.commit()


class SystemTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(SeleniumTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data()

        self.server_thread = threading.Thread(
            target=lambda: self.app.run(port=5001, use_reloader=False)
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists('selenium_test.db'):
            os.remove('selenium_test.db')

    def login(self):
        self.driver.get(f'{BASE_URL}/')
        self.driver.find_element(By.NAME, 'email').send_keys('selenium@plateful.com')
        self.driver.find_element(By.NAME, 'password').send_keys('testpassword')
        self.driver.find_element(By.CSS_SELECTOR, '#panel-login button[type=submit]').click()

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

    def test_explore_requires_login(self):
        self.driver.get(f'{BASE_URL}/explore')
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Unauthenticated access to /explore should redirect to login page')

    def test_explore_shows_recipes_after_login(self):
        self.login()
        self.driver.get(f'{BASE_URL}/explore')
        cards = self.driver.find_elements(By.CLASS_NAME, 'recipe-card')
        self.assertGreater(len(cards), 0,
                           'Explore page should show at least one recipe card after login')

    def test_logout_redirects_to_login(self):
        self.login()
        logout_form = self.driver.find_element(By.CSS_SELECTOR, 'form[action*="logout"]')
        logout_form.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        self.assertEqual(self.driver.current_url, f'{BASE_URL}/',
                         'Logout should redirect to the login page')


if __name__ == '__main__':
    unittest.main()
    