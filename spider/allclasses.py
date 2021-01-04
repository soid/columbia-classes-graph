# This is Scrapy crawler script that gets the data from Columbia University website, Wikipedia, culpa.info, etc

import json
import html
import scrapy
from scrapy import Request
from scrapy.selector import Selector
import urllib.parse
from w3lib.html import remove_tags
from helpers import *
import logging
logger = logging.getLogger(__name__)


class ClassesSpider(scrapy.Spider):
    TYPE_WIKI_LINK_PROFESSOR = "wiki_prof_link"

    name = 'all-classes'

    URLS_ = {
        # taken from http://bulletin.columbia.edu/general-studies/courses/
        'allclasses': 'http://bulletin.columbia.edu/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria=%7B%22department%22%3A%22%22%2C%22term%22%3A%223%22%2C%22level%22%3A%22%22%2C%22held%22%3A%22%22%2C%22begin%22%3A%22%22%2C%22end%22%3A%22%22%2C%22pl%22%3A%220%22%2C%22ph%22%3A%2210%22%2C%22keywords%22%3A%22%22%2C%22college%22%3A%22GS%22%7D',
        'Core: Global': 'http://bulletin.columbia.edu/general-studies/the-core/global-core/',
    }
    URLS_INVERT = {v: k for k, v in URLS_.items()}

    start_urls = list(URLS_.values())
    custom_settings = {
        # 'HTTPCACHE_ENABLED': False
        'HTTPCACHE_ENABLED': True
    }

    def parse(self, response):
        logger.info('Parse function called on %s', response.url)
        if ClassesSpider.URLS_INVERT[response.url] == 'allclasses':
            yield from self.parse_all_classes(response)
        else:
            logger.info('Identified as classes group: %s', ClassesSpider.URLS_INVERT[response.url])
            yield self.parse_classes_group(ClassesSpider.URLS_INVERT[response.url], response)

    def parse_all_classes(self, response):
        for course_html in response.css('results result description'):
            course = Selector(text=html.unescape(course_html.get()))

            course_data = parse_course(course)

            # crawl CULPA for instructors
            if len(course_data['instructors']) > 0:
                for instr in course_data['instructors']:
                    instr = instr.strip()
                    if not instr:
                        continue

                    # search professor on CULPA
                    url = 'http://culpa.info/search?utf8=✓&search=' \
                          + urllib.parse.quote_plus(instr) + '&commit=Search'
                    yield Request(url, callback=self.parse_culpa_search_prof,
                                  meta={'course_data': course_data,
                                        'instructor': instr})

                    # search class on CULPA
                    url = 'http://culpa.info/search?utf8=✓&search=' \
                          + urllib.parse.quote_plus(course_data['num']) + '&commit=Search'
                    yield Request(url, callback=self.parse_culpa_search_class,
                                  meta={'course_data': course_data})

                    # search professor on wikipedia
                    url = 'https://en.wikipedia.org/w/api.php?action=query&list=search&utf8=&format=json&srsearch=' \
                          + urllib.parse.quote_plus("Columbia University intitle:" + instr)
                    yield Request(url, callback=self.parse_wiki_prof,
                                  meta={'course_data': course_data,
                                        'instructor': instr})

            yield {**course_data, 'type': 'class'}

    """
    This function parses a list of classes group (only codes) in order to filter by only that group (e.g. the Core)
    """
    def parse_classes_group(self, classes_group, response):
        nums = [clear_utf_spaces(class_code)
                for class_code in response.css('.sc_courselist')[0].css('tr .codecol *::text').getall()]
        return {'classes-group': classes_group,
                'nums': nums,
                'type': 'classes_group'}

    # Parsing CULPA profs

    def parse_culpa_search_prof(self, response):
        found = response.css('.search_results .box tr td')
        if found:
            link = found.css('a::attr(href)').get()
            url = 'http://culpa.info' + link
            nugget = found.css('img.nugget::attr(alt)').get()
            yield Request(url, callback=self.parse_culpa_prof,
                          meta={**response.meta,
                                'link': link,
                                'nugget': nugget})

    def parse_culpa_prof(self, response):
        result = {
            'type': 'culpa_prof_link',
            'class': response.meta.get('course_data')['num'],
            'instructor': response.meta.get('instructor'),
            'count': len(response.css('div.professor .review')),
            'link': response.meta.get('link')
        }
        if response.meta.get('nugget'):
            if response.meta.get('nugget').upper().startswith("GOLD"):
                result['nugget'] = "gold"
            if response.meta.get('nugget').upper().startswith("SILVER"):
                result['nugget'] = "silver"
        yield result

    # Parsing CULPA classes

    def parse_culpa_search_class(self, response):
        found = response.css('.search_results .box tr td')
        if found:
            link = found.css('a::attr(href)').get()
            url = 'http://culpa.info' + link
            yield Request(url, callback=self.parse_culpa_class,
                          meta={**response.meta,
                                'link': link})

    def parse_culpa_class(self, response):
        yield {
            'type': 'culpa_course_link',
            'class': response.meta.get('course_data')['num'],
            'link': response.meta.get('link'),
            'count': len(response.css('div.course .review'))
        }

    # Wikipedia

    def parse_wiki_prof(self, response):
        instr = response.meta.get('instructor')
        json_response = json.loads(response.body_as_unicode())
        search = json_response['query']['search']
        logger.info('WIKI: Search results for %s : %s', instr, search)

        possible_match = []
        for result in search:
            title = result['title']
            if not ClassesSpider.validate_name(instr, title):
                continue

            if len(search) == 1:
                yield ClassesSpider.wiki_prof_link(instr, title)
                return

            snippet = remove_tags(result['snippet']).upper()
            if "COLUMBIA UNIVERSITY" not in snippet:
                possible_match.append(result)
                continue

            # found match
            yield ClassesSpider.wiki_prof_link(instr, title)
            return

        # follow some possible articles and try to understand if it's linked to profs
        for result in possible_match:
            url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote_plus(result['title'].replace(' ', '_'))
            yield Request(url, callback=self.parse_wiki_article_prof,
                          meta={**response.meta,
                                'instructor': instr,
                                'wiki_title': result['title']})

        logger.info('WIKI: Not found obvious wiki search results for %s. Following articles: %s',
                    instr, [x['title'] for x in possible_match])
        return

    @staticmethod
    def validate_name(instr, title):
        for name_part in instr.split(" "):
            if name_part not in title:
                return False
        return True

    @staticmethod
    def wiki_prof_link(instr, title):
        return {
            'type': ClassesSpider.TYPE_WIKI_LINK_PROFESSOR,
            'instructor': instr,
            'wiki_title': title
        }

    # Extended search of some articles: load the entire article
    def parse_wiki_article_prof(self, response):
        instr = response.meta.get('instructor')
        page = remove_tags(response.body_as_unicode()).upper()
        if "COLUMBIA UNIVERSITY" in page:
            return ClassesSpider.wiki_prof_link(instr, response.meta.get('wiki_title'))
        else:
            logger.info("WIKI: Rejecting article '%s'. Not linked to professor: %s",
                        response.meta.get('wiki_title'), instr)

