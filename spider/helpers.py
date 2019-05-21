
CLASS_RE = r'(([A-Z]{4})\s[A-Z]{1,2}\d+)\s(.+)$'


def parse_course(course):
    block_title = course.css('p.courseblocktitle strong::text')
    cls = block_title.re(CLASS_RE)
    return {
        'entry': block_title.getall(),
        'code': cls[1],
        'num': cls[0].replace("\u00a0", " "),
        'title': cls[2],
        'scheduled': True if course.css('div.desc_sched') else False,
        'points': "".join(course.css('p.courseblocktitle strong em::text').getall()),
        'prereq': "".join(course.css('span.prereq *::text').getall()).replace("\u00a0", " "),
        'descr': "".join(course.css('p.closed *::text').getall()),
    }
