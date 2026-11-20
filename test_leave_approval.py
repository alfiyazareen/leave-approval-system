"""
Automated UI Test Suite for Leave Approval System using Selenium WebDriver.
Supports testing against GitHub Pages, Vercel, or local index.html.

Requirements:
    pip install selenium webdriver-manager
Run command:
    python test_leave_approval.py
"""

import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

# Target URL: Default to live deployed URL or local file
TARGET_URL = os.environ.get(
    "APP_URL",
    "https://alfiyazareen.github.io/leave-approval-system/"
)

class LeaveApprovalSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("  STARTING SELENIUM TEST SUITE: LEAVE APPROVAL SYSTEM  ")
        print(f"  Target URL: {TARGET_URL}")
        print("=======================================================\n")

        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Uncomment to run in headless mode
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        if USE_WDM:
            cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            cls.driver = webdriver.Chrome(options=options)

        cls.wait = WebDriverWait(cls.driver, 10)
        cls.screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(cls.screenshots_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        time.sleep(2)
        cls.driver.quit()
        print("\n=======================================================")
        print("  ALL TESTS COMPLETED SUCCESSFULLY!                    ")
        print(f"  Screenshots saved in: {cls.screenshots_dir}")
        print("=======================================================\n")

    def setUp(self):
        self.driver.get(TARGET_URL)
        time.sleep(1)

    def take_screenshot(self, name):
        filepath = os.path.join(self.screenshots_dir, f"{name}.png")
        self.driver.save_screenshot(filepath)
        print(f"  📸 Screenshot saved: {name}.png")

    def test_01_verify_page_title(self):
        """TC01: Verify application loads with correct title"""
        print("\n[RUNNING] TC01: Verify Page Title")
        self.assertIn("Leave Approval System", self.driver.title)
        login_box = self.driver.find_element(By.ID, "loginBox")
        self.assertTrue(login_box.is_displayed())
        print("  ✅ [PASS] TC01: Page title & login container verified")

    def test_02_login_empty_username_validation(self):
        """TC02: Verify alert when username is submitted empty"""
        print("\n[RUNNING] TC02: Validate Empty Username")
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()

        # Handle JavaScript alert
        alert = self.wait.until(EC.alert_is_present())
        alert_text = alert.text
        self.assertIn("Enter username", alert_text)
        alert.accept()
        print("  ✅ [PASS] TC02: Alert caught with message: " + alert_text)

    def test_03_employee_apply_leave_success(self):
        """TC03: Employee login, apply leave, verify in Pending column"""
        print("\n[RUNNING] TC03: Employee Apply Leave")
        
        # 1. Fill login form
        username_input = self.driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys("Alfiya")

        role_select = Select(self.driver.find_element(By.ID, "role"))
        role_select.select_by_value("employee")

        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        # 2. Verify Employee dashboard appears
        employee_box = self.wait.until(EC.visibility_of_element_located((By.ID, "employeeBox")))
        self.assertTrue(employee_box.is_displayed())

        # 3. Fill leave details
        start_date = self.driver.find_element(By.ID, "startDate")
        end_date = self.driver.find_element(By.ID, "endDate")
        reason = self.driver.find_element(By.ID, "reason")

        start_date.send_keys("2026-12-01")
        end_date.send_keys("2026-12-05")
        reason.send_keys("Medical leave for family emergency")

        # 4. Click Apply Leave
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply Leave')]").click()

        # 5. Handle success alert
        alert = self.wait.until(EC.alert_is_present())
        self.assertIn("Leave applied!", alert.text)
        alert.accept()

        time.sleep(1)
        pending_box = self.driver.find_element(By.ID, "empPending")
        self.assertIn("Medical leave for family emergency", pending_box.text)

        self.take_screenshot("01_employee_pending_leave")
        print("  ✅ [PASS] TC03: Leave applied and displayed under Pending list")

    def test_04_manager_view_and_approve_leave(self):
        """TC04: Manager login, view pending request, approve it"""
        print("\n[RUNNING] TC04: Manager Approve Leave")

        # 1. First ensure a leave exists by submitting as Employee
        username_input = self.driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys("StudentA")
        Select(self.driver.find_element(By.ID, "role")).select_by_value("employee")
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        self.driver.find_element(By.ID, "startDate").send_keys("2026-12-10")
        self.driver.find_element(By.ID, "endDate").send_keys("2026-12-12")
        self.driver.find_element(By.ID, "reason").send_keys("Attending Project Workshop")
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply Leave')]").click()

        alert = self.wait.until(EC.alert_is_present())
        alert.accept()
        time.sleep(1)

        # 2. Click Back to return to Login
        back_btn = self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back")
        back_btn.click()

        # 3. Login as Manager
        user_field = self.wait.until(EC.visibility_of_element_located((By.ID, "username")))
        user_field.clear()
        user_field.send_keys("ManagerJane")
        Select(self.driver.find_element(By.ID, "role")).select_by_value("manager")
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        # 4. Verify Manager Dashboard
        manager_box = self.wait.until(EC.visibility_of_element_located((By.ID, "managerBox")))
        self.assertTrue(manager_box.is_displayed())

        # 5. Find Approve button in Pending section and click it
        approve_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#pendingLeaves .btn-approve")))
        approve_btn.click()

        time.sleep(1)
        # 6. Verify leave moved to Approved section
        approved_box = self.driver.find_element(By.ID, "approvedLeaves")
        self.assertIn("Attending Project Workshop", approved_box.text)

        self.take_screenshot("02_manager_approved_leave")
        print("  ✅ [PASS] TC04: Manager approved the leave and status updated to Approved")


if __name__ == "__main__":
    unittest.main(verbosity=2)
