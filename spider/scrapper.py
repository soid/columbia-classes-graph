import scrapy


class ClassesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://bulletin.columbia.edu/general-studies/undergraduates/majors-concentrations/computer-science/#coursestext',
    ]

    def parse(self, response):
        for course in response.css('div.courseblock'):
            blocktitle = course.css('p.courseblocktitle strong::text')
            yield {
                'num': blocktitle.re(r'\w+\s\w\d+'),
                'title': blocktitle.re(r'\w+\s\w\d+\s+(.+)$'),
                'scheduled': True if course.css('div.desc_sched') else False,
#                'class': blocktitle.get(),
                'points': course.css('p.courseblocktitle strong em::text').get(),
                'prereq': course.css('span.prereq *::text').getall(),
            }


