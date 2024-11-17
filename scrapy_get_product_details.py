import scrapy
from scrapy.crawler import CrawlerProcess
import os
import re
import json


def extract_brand(product_name):
    """
    Extracts the brand from the product name by keeping words until the first numeric word is found.
    """
    words = product_name.split()
    for i, word in enumerate(words):
        if re.search(r'\d', word):  # Check if the word contains a digit
            return ' '.join(words[:i])
    return ' '.join(words) # Return full name if no numeric word found

class ProductModelSpider(scrapy.Spider):
    name = 'product_spider'

    def start_requests(self):
        file_path = 'extracted_links.txt' 
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} not found in {os.getcwd()}.")
            return

        with open(file_path, 'r') as file:
            urls = [url.strip() for url in file.readlines()]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'TE': 'Trailers',
                },
                callback=self.parse
            )


    async def parse(self, response):
        model_number_xpath = "//div[contains(@aria-label, 'Model Number')]//p[last()]/text()"
        model_number_text = response.xpath(model_number_xpath).getall()
        if model_number_text:
            model_number = model_number_text[-1]
        else:
            model_number = "Model number not found"
        
        # XPath for product name
        product_name_xpath = "//h1[contains(@class, 'product-brand-description')]/text()"
        brand_name = extract_brand(response.xpath(product_name_xpath).get())

        price = "price not found"

        json_text = str(response.xpath("//script[contains(., 'mfePrice')]/text()").get())
        data = json.loads(json_text.split('=')[1])

        try:
            
            selling_price = data['productDetails'][next(iter(data['productDetails']))]['location']['price']['pricingDataList'][0]['finalPrice']
            price = selling_price
        except KeyError:
                price = 0


        # Printing to console for debugging
        print(f"Product Model Number: {model_number}")
        print(f"Product Brand: {brand_name}")
        print(f"Product Price: {price}")

        # Yielding the extracted data
        yield {
            'Product Model Number': model_number,
            'Product Name': brand_name or "Product name not found",
            'Product Price': price
        }

# Set up a process to run the spider
def run_spider():
    process = CrawlerProcess(settings={
        'FEED_URI': 'product_details.csv',
        'FEED_FORMAT': 'csv',
        'LOG_LEVEL': 'INFO',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    })
    
    process.crawl(ProductModelSpider)
    process.start()

run_spider()
