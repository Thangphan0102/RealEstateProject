import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy_repo.items import MogiVnItem


class MogiVnSpider(RedisSpider):
    name = "mogi_vn"
    redis_key = "mogi_vn_queue:start_urls"
    redis_batch_size = 10
    max_idle_time = 7

    def parse(self, response, **kwargs):
        property_item_links = response.css('ul.props li div.prop-info a.link-overlay::attr(href)').getall()
        yield from response.follow_all(property_item_links, callback=self.parse_property)

    def parse_property(self, response):
        property_item = MogiVnItem()

        property_item["title"] = response.css('div.main-info div.title h1::text').get()
        property_item["address"] = response.css('div.main-info div.address::text').get()
        property_item["price"] = response.css('div.main-info div.price::text').get()
        property_item["content"] = response.css('div.main-info div.info-content-body::text').getall()
        property_item["additional_info"] = response.css('div.main-info div.info-attrs div.info-attr span::text').getall()

        yield property_item