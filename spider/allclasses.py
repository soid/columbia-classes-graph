import html
import scrapy
from scrapy.selector import Selector
from helpers import parse_course


class ClassesSpider(scrapy.Spider):
    name = 'all-classes'
    start_urls = [
        # taken from http://bulletin.columbia.edu/general-studies/undergraduates/courses/?term=3&pl=0&ph=10&college=GS
        'http://bulletin.columbia.edu/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria=%7B%22department%22%3A%22%22%2C%22term%22%3A%223%22%2C%22level%22%3A%22%22%2C%22held%22%3A%22%22%2C%22begin%22%3A%22%22%2C%22end%22%3A%22%22%2C%22pl%22%3A%220%22%2C%22ph%22%3A%2210%22%2C%22keywords%22%3A%22%22%2C%22college%22%3A%22GS%22%7D',
    ]

    def parse(self, response):
        for course_html in response.css('results result description'):
            course = Selector(text=html.unescape(course_html.get()))

            yield parse_course(course)
