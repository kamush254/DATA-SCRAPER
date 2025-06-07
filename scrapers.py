# filepath: c:\Users\LENOVO\Desktop\scrape\maps_scraper\scrapers.py
import scrapy

class MySpider(scrapy.Spider):
    name = "myspider"
    start_urls = [
        "https://www.google.com/maps/search/restaurants+in+Nairobi",
        "https://www.google.com/maps/search/hotels+in+Mombasa",
        "https://www.google.com/maps/search/cafes+in+Kisumu"
    ]

    def parse(self, response):
        for business in response.css(".hfpxzc"):  # Replace with the correct CSS selector
            yield {
                "title": business.css(".dbg0pd::text").get(),  # Replace with the correct CSS selector
                "url": business.css(".aogddb::attr(href)").get()  # Replace with the correct CSS selector
            }