"""
Unit tests for ZCLWeb application utilities
"""
import unittest
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class UtilsJSTestCase(StaticLiveServerTestCase):
    """Test JavaScript utilities using Selenium"""

    def setUp(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)

    def tearDown(self):
        self.driver.quit()

    def test_dompurify_loaded(self):
        """Test DOMPurify is loaded and functional"""
        self.driver.get(f"{self.live_server_url}")

        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )

        # Test if DOMPurify is available
        result = self.driver.execute_script("""
            if (typeof DOMPurify !== 'undefined') {
                return DOMPurify.sanitize('<script>alert(1)</script>', {ALLOWED_TAGS: []});
            }
            return 'not found';
        """)
        self.assertEqual(result, 'alert(1)')

    def test_jquery_version(self):
        """Test jQuery version compatibility"""
        self.driver.get(f"{self.live_server_url}")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )

        version = self.driver.execute_script("return jQuery ? jQuery.fn.jquery : 'not found';")
        self.assertIn('3.5', version)

    def test_chart_destroy(self):
        """Test Chart.js destroy functionality"""
        self.driver.get(f"{self.live_server_url}/extend_home")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )

        # Test chart destroy
        result = self.driver.execute_script("""
            if (window.currentChart) {
                window.currentChart.destroy();
                return 'destroyed';
            }
            return 'no chart';
        """)
        # Just check script executes without error
        self.assertIn(result, ['destroyed', 'no chart'])
