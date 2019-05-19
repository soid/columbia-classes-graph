import scrapy


class ClassesSpider(scrapy.Spider):
    name = 'cs-classes'
    start_urls = [
        'http://bulletin.columbia.edu/general-studies/undergraduates/majors-concentrations/computer-science/#coursestext',
    ]

    def parse(self, response):
        for course in response.css('div.courseblock'):
            blocktitle = course.css('p.courseblocktitle strong::text')
            yield {
                'num': blocktitle.re(r'[A-Z]{4}\s[A-Z]{1,2}\d+')[0],
                'title': blocktitle.re(r'[A-Z]{4}\s[A-Z]{1,2}\d+\s+(.+)$'),
                'scheduled': True if course.css('div.desc_sched') else False,
                'points': course.css('p.courseblocktitle strong em::text').get(),
                'prereq': course.css('span.prereq *::text').getall(),
            }


