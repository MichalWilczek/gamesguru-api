import logging
import re
from enum import Enum
from urllib.parse import quote

from pydantic import ValidationError

from gamesguru.scraping import scrap_webpage
from .models import Shop, Product
from .schemas import OfferSchemaIn


_logger = logging.getLogger(__name__)


class ShopMetadata:
    pass


class MediaExpert(ShopMetadata):
    host = "https://www.mediaexpert.pl"
    url = f"{host}/search?query[menu_item]=&query[querystring]"
    offer_box_name = "offer-box"
    name_element_name = None
    price_box_name = "price-box"
    price_value_name = "whole"
    price_currency_name = "currency"


class RTVEuroAGD(ShopMetadata):
    host = "www.euro.com.pl"
    url = f"https://{host}/search.bhtml?keyword"
    offer_box_name = "box-medium"
    name_element_name = None
    price_box_name = "box-medium__price"
    price_value_name = "price-template__large--total"
    price_currency_name = "price-template__large--currency"


class MediaMarkt(ShopMetadata):
    host = "mediamarkt.pl"
    url = f"https://{host}/search?query%5Bmenu_item%5D=&query%5Bquerystring%5D"
    offer_box_name = "offer"
    name_element_name = None
    price_box_name = "price-box"
    price_value_name = "whole"
    price_currency_name = "currency"


class NeoNet(ShopMetadata):
    host = "www.neonet.pl"
    url = f"https://{host}/search.html?order=score&query"
    offer_box_name = "listingItemScss-root"
    name_element_name = "listingItemHeaderScss-name_limit"
    price_box_name = "uiPriceScss-price"
    price_value_name = "uiPriceScss-integer"
    price_currency_name = "uiPriceScss-currency"


class Empik(ShopMetadata):
    host = "www.empik.com"
    url = f"https://{host}/szukaj/produkt?q"
    offer_box_name = "search-list-item"
    name_element_name = None
    price_box_name = "price ta-price-tile"
    price_value_name = None
    price_currency_name = None


class OleOle(ShopMetadata):
    host = "www.oleole.pl"
    url = f"https://{host}/search.bhtml?keyword"
    # TODO: Add configuration
    offer_box_name = "box-medium"
    name_element_name = None
    price_box_name = None
    price_value_name = None
    price_currency_name = None


class ShopEnum(str, Enum):
    empik = 'Empik'
    media_expert = 'MediaExpert'
    media_markt = 'Media Markt'
    neonet = 'Neonet'
    ole_ole = 'OleOle'
    rtv_euro_agd = 'RTV EURO AGD'


def run_scraping(shop: Shop, product: Product) -> list[OfferSchemaIn] | None:
    try:
        match shop.name:
            case ShopEnum.empik.value:
                return scrap_offers(product, Empik())
            case ShopEnum.media_expert.value:
                return scrap_offers(product, MediaExpert())
            case ShopEnum.media_markt.value:
                return scrap_offers(product, MediaMarkt())
            case ShopEnum.neonet.value:
                return scrap_offers(product, NeoNet())
            case ShopEnum.rtv_euro_agd.value:
                return scrap_offers(product, RTVEuroAGD())
            case other:
                raise NameError()

    except NameError:
        _logger.error(f"Shop: {shop.name} does not have any searching algorithm implemented. Skipping.")
        return []
    except BaseException:
        _logger.warning(f'Shop: {shop.name}, Product: {product.name}. Unexpected error. Skipping.')


def scrap_offers(product: Product, metadata: ShopMetadata):
    try:
        search_name = quote(f"{product.category.name} {product.search_name}")
        soup = scrap_webpage(f"{metadata.url}={search_name}")
        offers = soup.find_all(class_=re.compile(metadata.offer_box_name))
    except BaseException as e:
        _logger.error(f"Unexpected error while querying chromedriver. Skipping. Error: {e}")
        return []

    results = []
    for box in offers:
        try:
            link_element = box.find('a', href=re.compile(product.base_name))
            link = f"{metadata.host}{link_element['href']}"

            name = get_offer_name(box, link_element, metadata)
            price_value, price_currency = get_prices(box, metadata)

            results.append(OfferSchemaIn(
                name=name,
                price=price_value,
                currency=price_currency,
                url=link
            ))

        except ValidationError:
            _logger.error(f"offer element: {box} not validated. Skipping...")
        except BaseException:
            _logger.debug(f"Unexpected error for offer element. Probably formatting not possible.")

    return results


def get_offer_name(box, link_element, metadata: ShopMetadata) -> str:
    if metadata.name_element_name:
        name_element = box.find(class_=re.compile(metadata.name_element_name))
    else:
        name_element = link_element

    name = remove_ascii_characters(name_element.text.strip())
    if not name:
        name = remove_ascii_characters(name_element.attrs['title'].strip())
    if not name:
        raise ValueError()

    return name


def get_prices(box, metadata: ShopMetadata) -> tuple:
    try:
        price_element = box.find(class_=re.compile(metadata.price_box_name))
        price_value = price_element.find('span', class_=re.compile(metadata.price_value_name)).text
        price_currency = price_element.find('span', class_=re.compile(metadata.price_currency_name))
        if price_currency is None:
            price_currency = "zł"
        else:
            price_currency = price_currency.text
        price_value = float(''.join(price_value.split()))
        price_currency = ''.join(price_currency.split())
        return price_value, price_currency

    except BaseException:
        price_element = box.find(class_=re.compile(metadata.price_box_name))
        price_value, price_currency = price_element.text.split()
        if price_currency is None:
            price_currency = "zł"
        price_value = float(price_value.replace(',', '.'))
        price_currency = ''.join(price_currency.split())
        return price_value, price_currency


def remove_ascii_characters(txt: str) -> str:
    return re.sub(r'[^\x00-\x7F]+', ' ', txt)
