import html
import scrapy
from scrapy.selector import Selector


class ClassesSpider(scrapy.Spider):
    name = 'all-classes'
    start_urls = [
        'http://bulletin.columbia.edu/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria=%7B%22department%22%3A%22%22%2C%22term%22%3A%223%22%2C%22level%22%3A%22%22%2C%22held%22%3A%22%22%2C%22begin%22%3A%22%22%2C%22end%22%3A%22%22%2C%22pl%22%3A%220%22%2C%22ph%22%3A%2210%22%2C%22keywords%22%3A%22%22%2C%22college%22%3A%22GS%22%7D',
    ]

    def parse(self, response):
        for course_html in response.css('results result description'):
            course = Selector(text=html.unescape(course_html.get()))

            blocktitle = course.css('p.courseblocktitle strong::text')
            yield {
                'entry': blocktitle.getall(),
                'num': blocktitle.re(r'[A-Z]{4}\s[A-Z]{1,2}\d+')[0],
                'title': blocktitle.re(r'[A-Z]{4}\s[A-Z]{1,2}\d+\s+(.+)$'),
                'scheduled': True if course.css('div.desc_sched') else False,
                'points': course.css('p.courseblocktitle strong em::text').get(),
                'prereq': course.css('span.prereq *::text').getall(),
            }

