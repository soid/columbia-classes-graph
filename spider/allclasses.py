import html
import scrapy
from scrapy import Request
from scrapy.selector import Selector
import urllib.parse
from helpers import parse_course


class ClassesSpider(scrapy.Spider):
    name = 'all-classes'
    start_urls = [
        # taken from http://bulletin.columbia.edu/general-studies/undergraduates/courses/?term=3&pl=0&ph=10&college=GS
        'http://bulletin.columbia.edu/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria=%7B%22department%22%3A%22%22%2C%22term%22%3A%223%22%2C%22level%22%3A%22%22%2C%22held%22%3A%22%22%2C%22begin%22%3A%22%22%2C%22end%22%3A%22%22%2C%22pl%22%3A%220%22%2C%22ph%22%3A%2210%22%2C%22keywords%22%3A%22%22%2C%22college%22%3A%22GS%22%7D',
    ]
    custom_settings = {
        'HTTPCACHE_ENABLED': True
    }

    def parse(self, response):
        for course_html in response.css('results result description'):
            course = Selector(text=html.unescape(course_html.get()))

            course_data = parse_course(course)

            # crawl CULPA for instructors
            if len(course_data['instructors']) > 0:
                for instr in course_data['instructors']:
                    url = 'http://culpa.info/search?utf8=✓&search=' \
                          + urllib.parse.quote_plus(instr) + '&commit=Search'
                    yield Request(url, callback=self.parse_culpa_search,
                                  meta={'course_data': course_data,
                                        'instructor': instr})
            yield {**course_data, 'type': 'class'}

    def parse_culpa_search(self, response):
        found = response.css('.search_results .box tr td')
        if found:
            link = found.css('a::attr(href)').get()
            url = 'http://culpa.info' + link
            yield Request(url, callback=self.parse_culpa_profile,
                          meta={**response.meta, 'link': link})

    def parse_culpa_profile(self, response):
        yield {
            'type': 'culpa_link',
            'class': response.meta.get('course_data')['num'],
            'instructor': response.meta.get('instructor'),
            'count': len(response.css('div.professor .review')),
            'link': response.meta.get('link')
        }
