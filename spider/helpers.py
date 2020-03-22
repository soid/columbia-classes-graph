import logging
import re

logger = logging.getLogger(__name__)

CLASS_RE = r'(([A-Z]{4})\s[A-Z]{1,2}\d+)\s(.+)$'


def parse_course(course):
    block_title = course.css('p.courseblocktitle strong::text')
    cls = block_title.re(CLASS_RE)
    logger.info('Parsing class: %s', cls)

    # scan instructors
    semester = None
    instructors = set()
    schedule = {}
    for sched_row in course.css('.desc_sched tr'):
        header = sched_row.css('.desc_sched_header strong::text')
        if len(header) > 0:
            # it's a header
            semester = clear_utf_spaces(header.getall()[0]).split(":")[0]
            continue

        columns = sched_row.css('td.unifyRow1')
        logger.info("Parsed the following columns: %s", [c.get for c in columns])
        if len(columns) > 2:
            instructor_col = columns[3].css("*::text").get()
            section_instructors = []
            if instructor_col:
                section_instructors = [x.strip() for x in instructor_col.split(",")]
                instructors.update(section_instructors)

            time_col = columns[2].css("*::text").get()
            if time_col:
                assert semester is not None
                if semester not in schedule:
                    schedule[semester] = []
                schedule[semester].append([section_instructors, time_col])

    return {
        'entry': block_title.getall(),
        'code': cls[1],
        'num': clear_utf_spaces(cls[0]),
        'title': cls[2],
        'scheduled': True if course.css('div.desc_sched') else False,
        'schedule': schedule,
        'points': "".join(course.css('p.courseblocktitle strong em::text').getall()),
        'prereq': clear_utf_spaces("".join(course.css('span.prereq *::text').getall())),
        'descr': "".join(course.css('p.closed *::text').getall()),
        'instructors': instructors
    }


def clear_utf_spaces(num):
    return num.replace("\u00a0", " ")


SEMESTER_NAME_TO_MONTH_NUMBER = {
    "SPRING": "1",
    "SUMMER": "2",
    "FALL": "3"
}
SEMESTER_NAME_TO_MONTH_NUMBER_REVERSE = {n: m for m, n in SEMESTER_NAME_TO_MONTH_NUMBER.items()}

RE_FILENAME = r"data-(\d{4})-(\d)\.json"


# data-2019-1.json -> Spring 2019
def get_semester_by_filename(filename):
    m = re.match(r"data-(\d{4})-(\d)\.json", filename)
    assert m
    year = m.group(1)
    month = m.group(2)
    return SEMESTER_NAME_TO_MONTH_NUMBER_REVERSE[month].capitalize() + " " + year


# sort semesters by name, e.g. Fall 2019 < Spring 2020
def sort_semesters(semesters):
    def replace_semester(semester_string):
        month, year = semester_string.split(" ")
        return year + "-" + SEMESTER_NAME_TO_MONTH_NUMBER[month.upper()]
    sem_dict = {replace_semester(k): k for k in semesters}
    lst = list(sem_dict.keys())
    lst.sort()
    return [sem_dict[l] for l in lst]
