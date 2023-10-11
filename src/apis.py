import logging
import time
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from pydantic import ValidationError

from src.schemas import ElementData

_logger = logging.getLogger(__name__)


MEDIA_EXPERT_HOST = "https://www.mediaexpert.pl"
MEDIA_EXPERT_URL = f"{MEDIA_EXPERT_HOST}/search?query[menu_item]=&query[querystring]=playstation%20"


async def scrap_page(url: str) -> str:
    driver = webdriver.Chrome()
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


async def get_media_expert_data() -> list[ElementData] | None:
    html_source = await scrap_page(MEDIA_EXPERT_URL)
    if html_source is None:
        return None

    soup = BeautifulSoup(html_source)
    offer_boxes = soup.find_all(class_=re.compile("offer-box"))

    results = []
    for box in offer_boxes:
        link_element = box.find('a', href=re.compile('playstation'))

        link = f"{MEDIA_EXPERT_HOST}{link_element['href']}"
        name = link_element.text.strip()

        price_element = box.find(class_=re.compile("price-box"))
        price_value = price_element.find('span', class_=re.compile("whole")).text
        price_currency = price_element.find('span', class_=re.compile("currency")).text

        price_value = float(''.join(price_value.split()))
        price_currency = ''.join(price_currency.split())

        try:
            results.append(ElementData(
                name=name,
                link=link,
                price=price_value,
                currency=price_currency
            ))
        except ValidationError:
            pass

    return results


if __name__ == '__main__':
    import asyncio
    asyncio.run(get_media_expert_data())
