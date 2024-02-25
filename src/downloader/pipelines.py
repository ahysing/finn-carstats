# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import FinnAd
from downloader.spiders.spider import Downloader

class DownloaderPipeline:
    def process_item(self, item: FinnAd, spider: Downloader) -> FinnAd:
        return item
