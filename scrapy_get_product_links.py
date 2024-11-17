import scrapy
import os

class LinkExtractor(scrapy.Spider):
    name = 'link_extractor'
    # Define the file to store links
    file_name = 'extracted_links.txt'
    base_url = 'https://www.lowes.com'  # Define base URL for concatenation

    def start_requests(self):
        # Loop through the file names based on known pattern
        for i in range(7):  # Assuming you have files from page_0.html to page_6.html
            filepath = f'file://{os.path.join(os.getcwd(), f"html_pages/page_{i}.html")}'
            yield scrapy.Request(url=filepath, callback=self.parse)

    def parse(self, response):
        # Extracting links using the provided CSS selector
        links = response.css('a[data-clicktype="product_tile_click"]::attr(href)').getall()
        unique_links = set(links)  # Use set to avoid duplicates

        # Open the file in append mode and write the links
        with open(self.file_name, 'a+') as file:
            for link in unique_links:
                # Check if link is relative and prepend base_url if needed
                if link.startswith('/'):
                    full_link = self.base_url + link
                else:
                    full_link = link
                file.write(f"{full_link}\n")  # Write each link on a new line

        # Log the count of unique links found
        self.log(f'Appended {len(unique_links)} unique links from {response.url} to {self.file_name}')

# Run the spider
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess(settings={
    'LOG_LEVEL': 'INFO',  # Set logging level to reduce clutter
})
process.crawl(LinkExtractor)
process.start()
