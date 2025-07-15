import scrapy
import urllib.parse

class KolodnyTPSSpider(scrapy.Spider):
    name = "kolodny_tps"
    allowed_domains = ["truepeoplesearch.com"]
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
    }
    start_urls = [
        "https://www.truepeoplesearch.com/results?name=Kolodny"
    ]

    def parse(self, response):
        # Find all result cards
        for person in response.css('.card-summary'):
            yield {
                "name": person.css('.h4 span::text').get(),
                "age": person.css('.content-value::text').re_first(r"\d+"),
                "known_cities": person.css('.content-row .link-to-more::text').getall(),
                "current_address": person.css('.content-row a.link-to-more span::text').get(),
                "possible_relatives": person.css('.card-content .card-link span::text').getall(),
                # Note: phone numbers usually only on detail pages
            }
            # Follow link to detail page for more info
            detail_url = person.css('a::attr(href)').get()
            if detail_url:
                yield response.follow(detail_url, self.parse_detail)

        # Handle pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_detail(self, response):
        phones = response.css('span.content-value[data-tp-field="Phone"]::text').getall()
        addresses = response.css('span.content-value[data-tp-field="Address"]::text').getall()
        relatives = response.css('div#relatives-section .link-to-more::text').getall()
        yield {
            "detail_url": response.url,
            "phone_numbers": phones,
            "addresses": addresses,
            "possible_relatives": relatives,
        }
