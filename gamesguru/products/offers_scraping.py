import logging
import re
from enum import Enum
from urllib.parse import quote

from pydantic import ValidationError

from gamesguru.scraping import scrap_webpage
from .models import Shop, Product, Offer
from .schemas import OfferSchemaIn


_logger = logging.getLogger(__name__)


class ShopMetadata:
    pass


class MediaExpert(ShopMetadata):
    host = "www.mediaexpert.pl"
    url = "https://{host}/search?query[menu_item]=&query[querystring]={search_name}"
    offer_box_name = "offer-box"
    name_element_name = None
    price_box_name = "price-box"
    price_value_name = "whole"
    price_currency_name = "currency"
    basket_text = "do koszyka"


class RTVEuroAGD(ShopMetadata):
    host = "www.euro.com.pl"
    url = "https://{host}/search.bhtml?keyword={search_name}"
    # url = "https://{host}/search,a1.bhtml?keyword={search_name}"  # a1 - tylko dostępne w internecie
    offer_box_name = "box-medium"
    name_element_name = None
    price_box_name = "box-medium__price"
    price_value_name = "price-template__large--total"
    price_currency_name = "price-template__large--currency"
    basket_text = "do koszyka"


class MediaMarkt(ShopMetadata):
    host = "mediamarkt.pl"
    url = "https://{host}/search?query%5Bmenu_item%5D=&query%5Bquerystring%5D={search_name}"
    offer_box_name = "offer"
    name_element_name = None
    price_box_name = "price-box"
    price_value_name = "whole"
    price_currency_name = "currency"
    basket_text = "do koszyka"


class NeoNet(ShopMetadata):
    host = "www.neonet.pl"
    url = "https://{host}/search.html?order=score&query={search_name}"
    # url = "https://{host}/search.html?order=score&query={search_name}&dostepnosc=do_24h"
    offer_box_name = "listingItemScss-root"
    name_element_name = "listingItemHeaderScss-name_limit"
    price_box_name = "uiPriceScss-price"
    price_value_name = "uiPriceScss-integer"
    price_currency_name = "uiPriceScss-currency"
    basket_text = "do koszyka"


class Empik(ShopMetadata):
    host = "www.empik.com"
    url = "https://{host}/szukaj/produkt?q={search_name}"
    # url = "https://{host}/szukaj/produkt?q={search_name}&availabilityLabel=do+72h"
    offer_box_name = "search-list-item"
    name_element_name = None
    price_box_name = "price ta-price-tile"
    price_value_name = None
    price_currency_name = None
    basket_text = "do koszyka"


class OleOle(ShopMetadata):
    host = "www.oleole.pl"
    url = f"https://{host}/search.bhtml?keyword"
    # TODO: Add configuration
    offer_box_name = "box-medium"
    name_element_name = None
    price_box_name = None
    price_value_name = None
    price_currency_name = None
    basket_text = None


class ShopEnum(str, Enum):
    empik = 'Empik'
    media_expert = 'Media Expert'
    media_markt = 'MediaMarkt'
    neonet = 'Neonet'
    ole_ole = 'OleOle'
    rtv_euro_agd = 'RTV EURO AGD'


def get_metadata(shop: Shop) -> ShopMetadata | None:
    try:
        match shop.name:
            case ShopEnum.empik.value:
                return Empik()
            case ShopEnum.media_expert.value:
                return MediaExpert()
            case ShopEnum.media_markt.value:
                return MediaMarkt()
            case ShopEnum.neonet.value:
                return NeoNet()
            case ShopEnum.rtv_euro_agd.value:
                return RTVEuroAGD()
            case other:
                raise NameError()
    except NameError:
        _logger.error(f"Shop: {shop.name} not implemented. Skipping.")
    except BaseException:
        _logger.warning(f'Shop: {shop.name}. Unexpected error. Skipping.')


def run_scraping(shop: Shop, product: Product) -> list[OfferSchemaIn] | None:
    metadata = get_metadata(shop)
    if metadata is None:
        _logger.error(f"Shop: {shop.name} does not have any scraping algorithm implemented. Skipping.")
        return []
    try:
        return scrap_offers(product, metadata)
    except BaseException:
        _logger.warning(f'Shop: {shop.name}, Product: {product.name}. Unexpected error. Skipping.')


def scrap_offer_for_validity(offer: Offer) -> bool | None:
    metadata = get_metadata(offer.shop)
    if metadata is None:
        _logger.error(f"Shop: {offer.shop.name} does not have any scraping algorithm implemented. Skipping.")
        return

    url = offer.url
    if 'https://' not in url:
        url = f'https://{url}'
    soup = scrap_webpage(url)
    basket_name = soup.find(string=re.compile(metadata.basket_text, re.IGNORECASE))
    if basket_name and len(basket_name) < 200:
        return True
    return False


def scrap_offers(product: Product, metadata: ShopMetadata):
    try:
        url = metadata.url.format(
            host=metadata.host,
            search_name=quote(product.search_name)
        )
        soup = scrap_webpage(url)
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
            if any(word.lower() in name.lower() for word in product.search_words_to_exclude_list):
                continue
            if not any(word.lower() in name.lower() for word in product.search_words_to_include_list):
                continue

            price_value, price_currency = get_prices(box, metadata)
            basket_name = box.find(string=re.compile(metadata.basket_text, re.IGNORECASE)).strip()
            if not basket_name:
                continue

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
    return txt.replace('\x00', ' ')
