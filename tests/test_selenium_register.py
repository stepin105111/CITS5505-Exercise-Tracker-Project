import time
import unittest
import multiprocessing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from app import create_application
from app.config import TestingConfig
from app.extensions import db
from app.database import User

localHost = "http://127.0.0.1:5000"

def run_test_server():
    app = create_application(TestingConfig)
    app.run(debug=False, use_reloader=False)


class SeleniumRegisterTest(unittest.TestCase):
    def setUp(self):
        # Start Flask server 
        self.server = multiprocessing.Process(target=run_test_server)
        self.server.start()
        time.sleep(2)  

        # Setup DB
        self.app = create_application(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create existing user for duplicate test
        existing_user = User(username="existinguser", email="exist@example.com")
        existing_user.set_password("password123")
        db.session.add(existing_user)
        db.session.commit()

        # Start browser
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.server.terminate()
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_registration(self):
        self.driver.get(localHost + "/register")

        self.driver.find_element(By.NAME, "username").send_keys("newuser")
        self.driver.find_element(By.NAME, "email").send_keys("newuser@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "secret_question").send_keys("first_pet")
        self.driver.find_element(By.NAME, "secret_answer").send_keys("Jacky")
        self.driver.find_element(By.NAME, "terms").click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_contains("/login")
        )
        self.assertIn("/login", self.driver.current_url)

    def test_duplicate_username(self):
        self.driver.get(localHost + "/register")

        self.driver.find_element(By.NAME, "username").send_keys("existinguser")
        self.driver.find_element(By.NAME, "email").send_keys("new@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "secret_question").send_keys("first_pet")
        self.driver.find_element(By.NAME, "secret_answer").send_keys("Buddy")
        self.driver.find_element(By.NAME, "terms").click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "error"))
        )

        error_text = self.driver.find_element(By.CLASS_NAME, "error").text
        self.assertIn("Username already exists", error_text)

    def test_duplicate_email(self):
        self.driver.get(localHost + "/register")

        self.driver.find_element(By.NAME, "username").send_keys("uniqueuser")
        self.driver.find_element(By.NAME, "email").send_keys("exist@example.com")  
        self.driver.find_element(By.NAME, "password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "secret_question").send_keys("first_pet")
        self.driver.find_element(By.NAME, "secret_answer").send_keys("Jacky")
        self.driver.find_element(By.NAME, "terms").click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "error"))
        )

        error_text = self.driver.find_element(By.CLASS_NAME, "error").text
        self.assertIn("Email already registered", error_text)
        
    def test_password_mismatch(self):
        self.driver.get(localHost + "/register")

        self.driver.find_element(By.NAME, "username").send_keys("wronguser")
        self.driver.find_element(By.NAME, "email").send_keys("wronguser@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Password123!")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("WrongPass!")
        self.driver.find_element(By.NAME, "secret_question").send_keys("first_pet")
        self.driver.find_element(By.NAME, "secret_answer").send_keys("Jacky")
        self.driver.find_element(By.NAME, "terms").click()
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 3).until(expected_conditions.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertEqual(alert.text, "Passwords do not match!")
        alert.accept()
if __name__ == '__main__':
    unittest.main()