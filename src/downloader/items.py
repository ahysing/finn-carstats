# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FinnAd(scrapy.Item):
    price = scrapy.Field(order=1)
    year = scrapy.Field()
    distance = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    search = scrapy.Field()
    first_registration = scrapy.Field()
    fuel = scrapy.Field()
    area = scrapy.Field()
