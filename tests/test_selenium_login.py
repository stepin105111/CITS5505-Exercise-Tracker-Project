import unittest
import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from app.extensions import db
from app.database import User
from app import create_application
from app.config import TestingConfig

localHost = "http://127.0.0.1:5000"

def run_test_server():
    app = create_application(TestingConfig)
    app.run(debug=False, use_reloader=False)
    
class SeleniumLoginTest(unittest.TestCase):

    def setUp(self):
        # Run server in subprocess
        self.server = multiprocessing.Process(target=run_test_server)
        self.server.start()
        time.sleep(2) 

        # Setup database
        self.app = create_application(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        test_user = User(username="testuser", email="test@example.com")
        test_user.set_password("testpass")
        db.session.add(test_user)
        db.session.commit()

        # Launch  browser
        options = webdriver.ChromeOptions()
       # options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)

        return super().setUp()

    def tearDown(self):
        self.server.terminate()
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        return super().tearDown()

    def test_login_success(self):
        self.driver.get(localHost + "/login")

        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_changes(localHost + "/login")
        )
        
        self.assertIn("/dashboard", self.driver.current_url)
    
    def test_navigate_to_register(self):
        self.driver.get(localHost + "/login")

        signup_link = self.driver.find_element(By.LINK_TEXT, "Sign up")
        signup_link.click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_contains("/register")
        )

        self.assertIn("/register", self.driver.current_url)
    
    def test_login_wrong_password(self):
        self.driver.get(localHost + "/login")

        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
         expected_conditions.presence_of_element_located((By.CLASS_NAME, "error"))
        )

        error_message = self.driver.find_element(By.CLASS_NAME, "error").text
        self.assertTrue("Invalid username or password" in error_message)
    
    def test_blank_login_submission(self):
        self.driver.get(localHost + "/login")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertIn("/login", self.driver.current_url)

        error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
        if error_elements:
            self.assertTrue(any("required" in el.text.lower() or "invalid" in el.text.lower() for el in error_elements))