import time
import urllib3

from bs4 import BeautifulSoup
from selenium import webdriver


def scrap_webpage(url: str) -> BeautifulSoup | None:
    html_source = get_url_data(url)
    if html_source is None:
        return None

    return BeautifulSoup(html_source, features="html.parser")


def get_url_data(url: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    )

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
    time.sleep(2)
    scroll_down(driver)
    html_source = driver.page_source
    driver.quit()
    return html_source


def scroll_down(driver, scroll_pause_time=2):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
