# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MogiVnItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    additional_info = scrapy.Field()
    content = scrapy.Field()
    address = scrapy.Field()
