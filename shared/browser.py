"""Selenium driver creation for remote containers and local development."""

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserUnavailableError(RuntimeError):
    """Raised when a Selenium browser session cannot be created."""


def create_driver():
    """Create a remote driver when configured, otherwise use local Chrome."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=800,600")

    selenium_url = os.getenv("SELENIUM_URL")
    try:
        if selenium_url:
            return webdriver.Remote(command_executor=selenium_url, options=options)
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
    except Exception as exc:
        location = selenium_url or "local Chrome"
        raise BrowserUnavailableError(
            f"Selenium browser is unavailable at {location}."
        ) from exc
