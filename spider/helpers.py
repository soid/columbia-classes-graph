
CLASS_RE = r'(([A-Z]{4})\s[A-Z]{1,2}\d+)\s(.+)$'


def parse_course(course):
    block_title = course.css('p.courseblocktitle strong::text')
    cls = block_title.re(CLASS_RE)

    # scan instructors
    instructors = set()
    for sched_row in course.css('.desc_sched tr'):
        rows = sched_row.css('td.unifyRow1')
        if len(rows) > 2:
            instructor_row = rows[3].css('*::text').get()
            if instructor_row:
                instructors.update([x.strip() for x in instructor_row.split(",")])

    return {
        'entry': block_title.getall(),
        'code': cls[1],
        'num': clear_class_num(cls[0]),
        'title': cls[2],
        'scheduled': True if course.css('div.desc_sched') else False,
        'points': "".join(course.css('p.courseblocktitle strong em::text').getall()),
        'prereq': clear_class_num("".join(course.css('span.prereq *::text').getall())),
        'descr': "".join(course.css('p.closed *::text').getall()),
        'instructors': instructors
    }


def clear_class_num(num):
    return num.replace("\u00a0", " ")
