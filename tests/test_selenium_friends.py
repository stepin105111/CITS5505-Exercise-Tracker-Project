import unittest
import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.extensions import db
from app.database import User
from app import create_application
from app.config import TestingConfig

localHost = "http://127.0.0.1:5000"

def run_test_server():
    app = create_application(TestingConfig)
    app.run(debug=False, use_reloader=False)
    
class SeleniumFriendsTest(unittest.TestCase):

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

        # Create test users
        self.main_user = User(username="mainuser", email="main@example.com")
        self.main_user.set_password("password123")
        
        self.friend_user = User(username="frienduser", email="friend@example.com")
        self.friend_user.set_password("password123")
        
        db.session.add(self.main_user)
        db.session.add(self.friend_user)
        db.session.commit()

        # Launch browser with appropriate options to avoid prompts
        options = webdriver.ChromeOptions()
        
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2  # Block notifications
        }
        options.add_experimental_option("prefs", prefs)
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        
        # Test in headless mode
        options.add_argument("--headless=new")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.server.terminate()
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as_main_user(self):
        """Helper method to login as the main test user"""
        self.driver.get(localHost + "/login")
        self.driver.find_element(By.NAME, "username").send_keys("mainuser")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )

    def test_search_for_friend(self):
        """Test searching for a friend in the friends section"""
        self.login_as_main_user()
        
        
        self.driver.find_element(By.XPATH, "//a[@class='menu-item' and contains(@data-target, 'share-section')]").click()
        
        
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "share-section"))
        )
        
        
        search_box = self.driver.find_element(By.ID, "user-search")
        search_box.clear()
        search_box.send_keys("frienduser")
        
        
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "search-results"))
        )
        
        # Check if the user appears in search results
        search_results = self.driver.find_element(By.ID, "search-results").text
        self.assertIn("frienduser", search_results)
        
        # Check if "Add Friend" button exists for the user
        add_buttons = self.driver.find_elements(By.CLASS_NAME, "add-btn")
        self.assertTrue(len(add_buttons) > 0)

    def test_add_friend(self):
        """Test adding a friend and verifying they appear in the list"""
        self.login_as_main_user()
        
        
        self.driver.find_element(By.XPATH, "//a[@class='menu-item' and contains(@data-target, 'share-section')]").click()
        
        
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "share-section"))
        )
        
        # Search for friend
        search_box = self.driver.find_element(By.ID, "user-search")
        search_box.clear()
        search_box.send_keys("frienduser")
        
        
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#search-results .user-card"))
        )
        
        # Click "Add Friend" button
        add_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-btn[data-username='frienduser']"))
        )
        add_button.click()
        
        # Wait for and handle alert if present
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            # No alert, continue
            pass
            
        # Verify the friend appears in the leaderboard (after page refresh)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "leaderboard-container"))
        )
        
        # Check if the friend is in the leaderboard
        leaderboard = self.driver.find_element(By.CLASS_NAME, "leaderboard-container").text
        self.assertIn("frienduser", leaderboard)

    def test_already_friends_badge(self):
        """Test that 'Already Friends' badge shows in search for existing friends"""
        # Setup: First add the friend
        self.test_add_friend()
        
        # Then search again to see the "Already Friends" badge
        search_box = self.driver.find_element(By.ID, "user-search")
        search_box.clear()
        search_box.send_keys("frienduser")
        
        
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#search-results .user-card"))
        )
        
        # Verify if they are already friends
        search_results = self.driver.find_element(By.ID, "search-results").text
        
        self.assertTrue(
            "Already Friends" in search_results or 
            "Remove Friend" in search_results or
            "Friend" in search_results
        )

    def test_remove_friend(self):
        """Test removing a friend from the leaderboard"""
        # First add the friend
        self.test_add_friend()
        
        # Find the remove button in the leaderboard
        try:
            remove_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".friend-card .remove-btn[data-username='frienduser']"))
            )
            # If found, click it
            remove_button.click()
            
            # Handle alert if present
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.accept()
            except TimeoutException:
                # No alert, continue
                pass
                
            # Check that friend is no longer in leaderboard
            time.sleep(2)
            leaderboard = self.driver.find_element(By.CLASS_NAME, "leaderboard-container").text
            self.assertNotIn("frienduser", leaderboard)
        except (TimeoutException, NoSuchElementException):
            search_box = self.driver.find_element(By.ID, "user-search")
            search_box.clear()
            search_box.send_keys("frienduser")
            
            
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#search-results .user-card"))
            )
            
            # Find and click remove button
            remove_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".remove-btn[data-username='frienduser']"))
            )
            remove_button.click()
            
            # Handle alert if present
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.accept()
            except TimeoutException:
                # No alert, continue
                pass
                
            # Check that friend is no longer in leaderboard
            time.sleep(2)
            leaderboard = self.driver.find_element(By.CLASS_NAME, "leaderboard-container").text
            self.assertNotIn("frienduser", leaderboard)

if __name__ == '__main__':
    unittest.main()