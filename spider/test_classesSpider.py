from unittest import TestCase
from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from scrapy import Request
from scrapy.http import HtmlResponse

from allclasses import ClassesSpider

with Betamax.configure() as config:
    # where betamax will store cassettes (http responses):
    config.cassette_library_dir = 'cassettes'
    config.preserve_exact_body_bytes = True


class TestClassesSpider(BetamaxTestCase):
    def test_parse_wiki_prof(self):
        # Michael Collins
        url = "https://en.wikipedia.org/w/api.php?action=query&list=search&utf8=&format=json&srsearch=Columbia+University+intitle%3AMichael+Collins"
        response = self.session.get(url)

        scrapy_response = HtmlResponse(body=response.content, url=url,
                                       request=Request(url, meta={'instructor': "Michael Collins"}))

        allclasses = ClassesSpider()
        result_generator = allclasses.parse_wiki_prof(scrapy_response)
        result = []
        for r in result_generator:
            result.append(r)
        assert len(result) == 1
        assert result[0]['instructor'] == "Michael Collins", result[0]
        assert result[0]['wiki_title'] == "Michael Collins (computational linguist)", result[0]
