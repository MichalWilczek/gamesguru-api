# TODO:
#  - Write tests for filtering out specific name patterns (use some exemplary names from searched webpages)

# TODO: Another MR
#  - Check why MediaMarkt & MediaExpert don't work
#  - Optionally, add Komputronik and Sferis

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
    name_element_name = None
    price_value_name = None
    price_currency_name = None
    scraping_ignore_basket = False


class MediaExpert(ShopMetadata):
    host = "www.mediaexpert.pl"
    url = "https://{host}/search?query[menu_item]=&query[querystring]={search_name}"
    offer_box_name = "offer-box"
    price_box_name = "price-box"
    price_value_name = "whole"
    price_currency_name = "currency"
    basket_text = "do koszyka"


class RTVEuroAGD(ShopMetadata):
    host = "www.euro.com.pl"
    url = "https://{host}/search.bhtml?keyword={search_name}"
    offer_box_name = "box-medium"
    price_box_name = "box-medium__price"
    price_value_name = "price-template__large--total"
    price_currency_name = "price-template__large--currency"
    basket_text = "do koszyka"


class MediaMarkt(ShopMetadata):
    host = "mediamarkt.pl"
    offer_box_name = "sc-78ebdf9c-0 duPMTS"
    price_box_name = "sc-e9a876bf-0 hlFEGZ"
    price_value_name = "sc-f1f881c4-0 eDRAfL sc-b5c27d99-2 fWQVGc"
    price_currency_name = None
    basket_text = "do koszyka"

    @property
    def url(self):
        link = f'https://{self.host}/pl/search.html'
        query = 'query={search_name}'
        # url = f'{link}?{query}'

        from datetime import datetime
        timestamp = f't={int(datetime.now().timestamp()*1000)}'
        url = f'{link}?{query}&{timestamp}&ga_{query}'
        # url = f'{link}?{query}&{timestamp}&ga_{query}&ga_queryHash=481cf0e512d45f91b2496f720b5fdec3626a8d78cdc7dbe305499e24a455aab6&ga_queryRequestId=481cf0e512d45f91b2496f720b5fdec3626a8d78cdc7dbe305499e24a455aab6'
        return url


class NeoNet(ShopMetadata):
    host = "www.neonet.pl"
    url = "https://{host}/search.html?order=score&query={search_name}"
    offer_box_name = "listingItemScss-root"
    name_element_name = "listingItemHeaderScss-name_limit"
    price_box_name = "uiPriceScss-price"
    price_value_name = "uiPriceScss-integer"
    price_currency_name = "uiPriceScss-currency"
    basket_text = "do koszyka"


class Empik(ShopMetadata):
    host = "www.empik.com"
    url = "https://{host}/szukaj/produkt?q={search_name}"
    offer_box_name = "search-list-item"
    price_box_name = "price ta-price-tile"
    basket_text = "Dodaj do koszyka"


class OleOle(ShopMetadata):
    host = "www.oleole.pl"
    url = "https://{host}/search,a1.bhtml?keyword={search_name}"
    offer_box_name = "product-box"
    price_box_name = "price-list"
    price_value_name = "total"
    price_currency_name = "currency"
    scraping_ignore_basket = True
    basket_text = "Do koszyka"


class Morele(ShopMetadata):
    host = "www.morele.net"
    url = "https://{host}/wyszukiwarka/?q={search_name}"
    offer_box_name = "cat-product card"
    price_box_name = "price-new"
    basket_text = "Do koszyka"


class ShopEnum(str, Enum):
    empik = 'Empik'
    media_expert = 'Media Expert'
    media_markt = 'MediaMarkt'
    neonet = 'Neonet'
    ole_ole = 'OleOle'
    rtv_euro_agd = 'RTV EURO AGD'
    morele = 'Morele'


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
            case ShopEnum.ole_ole.value:
                return OleOle()
            case ShopEnum.morele.value:
                return Morele()
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
    results = []
    non_repeated_offer_urls = []

    for search_name in product.search_names:
        try:
            url = metadata.url.format(
                host=metadata.host,
                search_name=quote(search_name)
            )
            soup = scrap_webpage(url)
            offers = soup.find_all(class_=re.compile(metadata.offer_box_name))
        except BaseException as e:
            _logger.error(f"Unexpected error while querying chromedriver. Skipping. Error: {e}")
            return []

        # a = soup.find('div', attrs={'data-test': 'mms-product-card'})
        #
        # print(len(soup.find_all(string=re.compile("data-test"))))
        #
        # soup.find_all(class_=re.compile('sc-78ebdf9c-0 duPMTS'))


        search_results = []
        for box in offers:
            try:
                for base_name in product.base_names:
                    link_element = box.find('a', href=re.compile(base_name))
                    if link_element:
                        break

                link = f"{metadata.host}{link_element['href']}"
                if link in non_repeated_offer_urls:
                    continue
                non_repeated_offer_urls.append(link)

                name = get_offer_name(box, link_element, metadata)
                if not is_name_valid(name, product):
                    continue

                price_value, price_currency = get_prices(box, metadata)
                if not metadata.scraping_ignore_basket:
                    basket_name = box.find(string=re.compile(metadata.basket_text, re.IGNORECASE)).strip()
                    if not basket_name:
                        continue

                search_results.append(OfferSchemaIn(
                    name=name,
                    price=price_value,
                    currency=price_currency,
                    url=link
                ))

            except ValidationError:
                _logger.error(f"offer element: {box} not validated. Skipping...")
            except BaseException:
                _logger.debug(f"Unexpected error for offer element. Probably formatting not possible.")

        results.extend(search_results)

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


def is_name_valid(name: str, product: Product) -> bool:
    if product.search_words_any_to_exclude:
        found_any_word_to_exclude = any(
            word.lower() in name.lower() for word in product.search_words_any_to_exclude)
        if found_any_word_to_exclude:
            return False

    if product.search_words_any_to_include:
        found_all_words_to_include = any(
            word.lower() in name.lower() for word in product.search_words_any_to_include)
        if not found_all_words_to_include:
            return False

    if product.search_words_all_to_include:
        found_all_words_to_include = all(
            word.lower() in name.lower() for word in product.search_words_all_to_include)
        if not found_all_words_to_include:
            return False

    return True


def get_prices(box, metadata: ShopMetadata) -> tuple:
    try:
        price_element = box.find(class_=re.compile(metadata.price_box_name))
        price_string = price_element.find('span', class_=re.compile(metadata.price_value_name)).text
        price_currency = price_element.find('span', class_=re.compile(metadata.price_currency_name))
        if price_currency is None:
            price_currency = "zł"
        else:
            price_currency = price_currency.text

        price_string = price_string.replace('\n', '')
        price_value = re.findall(r'[0-9., ]+', price_string)[0].replace(' ', '')
        price_value = price_value.replace(',', '.')
        price_value = float(price_value)

        price_currency = ''.join(price_currency.split())
        return price_value, price_currency

    except BaseException:
        price_element = box.find(class_=re.compile(metadata.price_box_name))

        price_string = price_element.text
        price_string = price_string.replace('\n', '')

        price_value = re.findall(r'[0-9., ]+', price_string)[0].replace(' ', '')
        currency_value = re.sub(r'[0-9.,]+', '', price_string)
        if currency_value:
            currency_value = currency_value.replace(' ', '')
        else:
            currency_value = 'zł'

        price_value = price_value.replace(',', '.')
        price_value = float(price_value)
        return price_value, currency_value


def remove_ascii_characters(txt: str) -> str:
    return txt.replace('\x00', ' ')
