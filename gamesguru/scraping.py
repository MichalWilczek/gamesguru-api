import time
import random

import urllib3
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver


def scrap_webpage(url: str) -> BeautifulSoup | None:
    html_source = get_url_data(url)
    if html_source is None:
        return None

    return BeautifulSoup(html_source, features="html.parser")


def get_url_data(url: str) -> str:
    user_agent = UserAgent()
    user_agent = user_agent.random

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument(f'--user-agent={user_agent}')

    # Try to connect to the running container 'chromedriver' through the docker network.
    try:
        driver = webdriver.Remote(
            command_executor='http://chromedriver:4444/wd/hub',
            options=options
        )

    # Other options mostly for debugging purposes.
    except urllib3.exceptions.MaxRetryError:
        try:
            driver = webdriver.Remote(
                command_executor='http://127.0.0.1:4444/wd/hub',
                options=options
            )
        except urllib3.exceptions.MaxRetryError:
            driver = webdriver.Chrome()

    driver.get(url)
    time.sleep(random.uniform(4, 6))
    scroll_down(driver)
    html_source = driver.page_source
    driver.quit()
    return html_source


def scroll_down(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(random.uniform(1, 2))

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
