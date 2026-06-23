#system tests
#install playwright for python 
#(pip install playwright
#playwright install)

import re
from playwright.sync_api import sync_playwright

def test_login_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5000/login")
        assert page.title() == "Login Page"
        browser.close()