from downloader.items import FinnAd
import scrapy
#from scrapy.crawler import CrawlerProcess
from pydantic import BaseModel
import logging
from urllib.parse import urlparse, quote_plus, parse_qs
import unicodedata
import re
import datetime

logger = logging.getLogger(__name__)


class Args(BaseModel):
    min_price: int | None = 0
    max_price: int | None = 0
    min_distance: int | None = 0
    max_distance: int | None = 0
    min_year: int | None = 0
    max_year: int | None = 0
    search: str = ''


class LinkGenerator(object):
    def __init__(self, args: Args):
        self.args = args
        self.start_url = ''

    def search(self) -> str:
        link = self.start_url + '?'
        if self.args.min_price:
            link += f'min_price={self.args.min_price}&'
        if self.args.max_price:
            link += f'max_price={self.args.max_price}&'
        if self.args.min_distance:
            link += f'min_distance={self.args.min_distance}&'
        if self.args.max_distance:
            link += f'max_distance={self.args.max_distance}&'
        if self.args.min_year:
            link += f'min_year={self.args.min_year}&'
        if self.args.max_year:
            link += f'max_year={self.args.max_year}&'
        link += f'q={quote_plus(self.args.search)}'
        return link

    def next(self, next: int) -> str:
        link = self.search()
        if link[-1] != '?':
            return f'{link}&page={next}'
        else:
            return f'{link}page={next}'


def clean_text(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.strip()
    return text


def clean_number(text: str) -> str:
    output = clean_text(text)
    return re.sub(r"\s+", "", output, flags=re.UNICODE)


class Downloader(scrapy.Spider):
    name = 'spiders'
    start_urls = ['https://www.finn.no/car/used/search.html']
    def __init__(self, *args1, **kwargs):
        super().__init__(*args1, **kwargs)
        min_price = kwargs.get('min_price') if kwargs.get('min_price') else 0
        max_price = kwargs.get('max_price') if kwargs.get('max_price') else 0
        min_distance = kwargs.get('min_distance') if kwargs.get('min_distance') else 0
        max_distance = kwargs.get('max_distance') if kwargs.get('max_distance') else 0
        min_year = kwargs.get('min_year') if kwargs.get('min_year') else 0
        max_year = kwargs.get('max_year') if kwargs.get('max_year') else 0
        search = kwargs.get('search')
        args = Args(
            min_price=min_price,
            max_price=max_price,
            min_distance=min_distance,
            max_distance=max_distance,
            min_year=min_year,
            max_year=max_year,
            search=search
        )
        self.args = args
        self.link_generator = LinkGenerator(args)


    def _get_next_page_number(self, response) -> int:
        parsed_url = urlparse(response.url)
        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            if 'page' in query:
                raw = query['page']
                for value in raw:
                    if value.isdigit():
                        return int(value) + 1
        return 1

    def parse(self, response):
        if response.status == 200:
            if response.url in self.start_urls:
                self.link_generator.start_url = response.url
                next_page_url = self.link_generator.search()
                yield scrapy.Request(next_page_url, callback=self.parse)
            else:
                found_cars = False
                page_results = response.css('#page-results')
                items = page_results.css('article')
                for item in items:
                    title_element = item.css('h2 a')
                    link = title_element.css('::attr(href)').get()
                    yield scrapy.Request(link, callback=self.parse)
                    found_cars = True
                if found_cars:
                    next_page_number = self._get_next_page_number(response)
                    next_page_url = self.link_generator.next(next_page_number)
                    yield scrapy.Request(next_page_url, callback=self.parse)
                else:
                    year = response.xpath('//div[contains(text(), "Modellår")]/following-sibling::div').css("::text").get()

                    distance = response.xpath('//div[contains(text(), "Kilometer")]/following-sibling::div').css("::text").get()

                    price_ex_vat = response.xpath('//dt[contains(text(), "Pris eks omreg")]/following-sibling::dd').css("::text").get()
                    price_registration = response.xpath('//dt[contains(text(), "Omregistrering")]/following-sibling::dd').css("::text").get()

                    first_registration = response.xpath('//dt[contains(text(), "1. gang registrert")]/following-sibling::dd').css("::text").get()

                    title = response.css('h1::text').get()
                    sub_title = response.xpath('//h1/following-sibling::p').css('::text').get()

                    fuel = response.xpath('//div[contains(text(), "Drivstoff")]/following-sibling::div').css("::text").get()
                    first_registration = datetime.datetime.strptime(first_registration, '%d.%m.%Y').strftime('%Y-%m-%d')

                    year = clean_number(year)
                    distance = clean_number(distance)
                    distance = distance.strip('km')
                    title = clean_text(title)
                    if sub_title:
                        title += " " + clean_text(sub_title)

                    fuel = clean_text(fuel)

                    if price_registration is None or "Fritatt" in price_registration:
                        price = response.xpath('//span[contains(text(), "Totalpris")]/following-sibling::span').css("::text").get()
                        price = clean_number(price)
                        price = price.strip('kr')
                    else:
                        price_ex_vat = clean_number(price_ex_vat)
                        price_ex_vat = price_ex_vat.strip('kr')

                        price_registration = clean_number(price_registration)
                        price_registration = price_registration.strip('kr')

                        price = int(price_ex_vat) + int(price_registration)

                    yield FinnAd(year=year, distance=distance, price=price, first_registration=first_registration, url=response.url, title=title, search=self.args.search, fuel=fuel)

        elif response.status == 404:
            logger.info(f'Found end of pagination')
        elif response.status > 299:
            logger.warning(f'Failed to download page {response.url} with status {response.status}')
        else:
            logger.info("ok")


#def main():
#    args = _parse_args()
#    process = CrawlerProcess()
#    process.crawl(Downloader, args=args)
#    logger.info('Starting')
#    process.start()
#    logger.info('Finished')


#if __name__ == '__main__':
#    main()