import scrapy
from helpers import parse_course


class ClassesSpider(scrapy.Spider):
    name = 'cs-classes'
    start_urls = [
        'http://bulletin.columbia.edu/general-studies/undergraduates/majors-concentrations/computer-science/#coursestext',
    ]

    def parse(self, response):
        for course in response.css('div.courseblock'):
            yield parse_course(course)
