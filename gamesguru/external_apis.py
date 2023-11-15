import logging
import time
import re
import urllib3

from selenium import webdriver
from bs4 import BeautifulSoup
from pydantic import ValidationError

from gamesguru.products.schemas import OfferSchemaIn

_logger = logging.getLogger(__name__)


MEDIA_EXPERT_HOST = "https://www.mediaexpert.pl"
MEDIA_EXPERT_URL = f"{MEDIA_EXPERT_HOST}/search?query[menu_item]=&query[querystring]=playstation%20"


def scrap_page(url: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')

    # Try to connect to the running container 'chromedriver' through the docker network.
    # The 'localhost' network is for debugging purposes when the service is not running in container.
    try:
        driver = webdriver.Remote(
            command_executor='http://chromedriver:4444/wd/hub',
            options=options
        )
    except urllib3.exceptions.MaxRetryError:
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=options
        )

    driver.get(url)
    time.sleep(2)
    scroll_down_page(driver)
    html_source = driver.page_source
    driver.quit()
    return html_source


def scroll_down_page(driver):
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_media_expert_data() -> list[OfferSchemaIn] | None:
    html_source = scrap_page(MEDIA_EXPERT_URL)
    if html_source is None:
        return None

    soup = BeautifulSoup(html_source, features="html.parser")
    offer_boxes = soup.find_all(class_=re.compile("offer-box"))

    results = []
    for box in offer_boxes:
        try:
            link_element = box.find('a', href=re.compile('playstation'))

            link = f"{MEDIA_EXPERT_HOST}{link_element['href']}"
            name = link_element.text.strip()

            price_element = box.find(class_=re.compile("price-box"))
            price_value = price_element.find('span', class_=re.compile("whole")).text
            price_currency = price_element.find('span', class_=re.compile("currency")).text

            price_value = float(''.join(price_value.split()))
            price_currency = ''.join(price_currency.split())

            results.append(OfferSchemaIn(
                name=name,
                price=price_value,
                currency=price_currency,
                url=link
            ))
        except ValidationError:
            _logger.error(f"offer element: {box} not validated. Skipping...")
        except BaseException as e:
            _logger.error(f"Unexpected error for offer element. Probably formatting not possible.")

    return results


if __name__ == '__main__':
    get_media_expert_data()
