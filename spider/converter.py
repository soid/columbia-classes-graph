import datetime
import re
import json
from os.path import dirname, realpath

from allclasses import ClassesSpider


class Converter:
    courseNumPattern = re.compile(r'^\w')

    @staticmethod
    def get_data():
        with open(dirname(dirname(realpath(__file__))) + '/data/all-classes.json', 'r') as file:
            return json.loads(file.read())

    def __init__(self):
        self.elements = {}
        self.elements['nodes'] = []
        self.elements['edges'] = []

        self.courses = {}
        self.culpa_links = {}
        self.codes = set()
        self.tmp_id = 1

    def add_course(self, course):
        course['num'] = course['num']
        if course['scheduled']:
            self.codes.add(course['code'])
            data = {
                # crawled
                **course,
                # derived
                **{
                    'id': course['num'],
                    'color': '#ABC4AB' if course['scheduled'] else 'grey',
                    'size': 50,
                }
            }
            del data['entry']
            del data['type']
            self.elements['nodes'].append({
                'data': data
            })
        self.courses[course['num']] = course

    def add_prereq(self, pre, num, code):
        pre = pre
        num = num
        c = self.fuzzy_find(pre)
        if not c:
            # class is not listed
            return
        elif c['num'] != pre:
            pre = c['num']

        if not self.courses[pre]['scheduled']:
            return

        if pre == num:
            return

        self.elements['edges'].append({
            'data': {
                'source': pre,
                'target': num,
                'code': code
            }
        })

    def parse(self, data):
        # create instructors index
        link_re = re.compile(r'\/(\d+)$')
        courses = []
        culpa_courses = {}
        for entry in data:
            if entry['type'] == 'class':
                courses.append(entry)
            if entry['type'] == 'culpa_prof_link':
                self.add_prof_info(entry['instructor'],
                                   count=entry['count'], culpa_id=link_re.search(entry["link"]).group(1))
                if 'nugget' in entry:
                    self.culpa_links[entry['instructor']]['nugget'] = entry['nugget']
            if entry['type'] == ClassesSpider.TYPE_WIKI_LINK_PROFESSOR:
                self.add_prof_info(entry['instructor'],
                                   wiki=entry["wiki_title"].replace(" ", "_"))
            if entry['type'] == 'culpa_course_link':
                culpa_courses[entry['class']] = {
                    'count': entry['count'],
                    'id': link_re.search(entry["link"]).group(1)
                }

        # create nodes
        for course in courses:
            if course['num'] in culpa_courses:
                course['culpa'] = culpa_courses[course['num']]
            title = course['title']
            num = course['num']
            print(num + " : " + title)
            self.add_course(course)
            
        # create edges
        for course in courses:
            num = course['num']
            prereq = self.retrieve_prereqs(course['prereq'])
            if course['scheduled']:
                for pre in prereq:
                    if type(pre) == list:
                        for p in pre:
                            self.add_prereq(p, num, course['code'])
                    else:
                        self.add_prereq(pre, num, course['code'])
                
        return self.elements

    def add_prof_info(self, instr, **kwargs):
        if instr not in self.culpa_links:
            self.culpa_links[instr] = {}
        for k, v in kwargs.items():
            self.culpa_links[instr][k] = v

    # some courses don't match exact characters. Try to find non-exact matches
    def fuzzy_find(self, num):
        if num in self.courses:
            return self.courses[num]
        for c in self.courses.keys():
            if num in c:
                return self.courses[c]
        return None

    PREREQ_PATTERN = re.compile(r'([A-Z]{4} [A-Z][A-Z]?[0-9]{4}|[A-Z][A-Z]?[0-9]{4}|[oO][rR]|[aA][nN][dD])')

    # Retrieves a list of prerequisites from a free text form
    @staticmethod
    def retrieve_prereqs(prereq_str):
        matches = Converter.PREREQ_PATTERN.findall(prereq_str)

        prereq = []
        mode = "and"
        for m in matches:
            if m.lower() == "or" and len(prereq) > 0:
                mode = "or"
            elif m.lower() == "and":
                mode = "and"
            else:
                if mode == "and":
                    if m.lower() != 'and' and m.lower() != 'or':
                        prereq.append(m)
                        mode = "and"
                else:
                    last = prereq[-1]
                    if type(last) == list:
                        last.append(m)
                    else:
                        prereq[-1] = [prereq[-1], m]
                    mode = "and"

        return prereq


if __name__ == "__main__":
    data = Converter.get_data()

    obj = Converter()
    elements = obj.parse(data)

    # write output
    f = open('data/classes-data.js', 'w')
    f.write("elements = ")
    f.write(json.dumps(elements))
    f.write(";\ngenerationDate = '" + datetime.datetime.now().strftime("%m/%d/%Y") + "';")

    # load codes mapper
    mf = open('spider/department-codes.json', 'r')
    code_mapper = json.loads(mf.read())
    mf.close()

    # generate a list of all codes
    codes = list(obj.codes)
    codes.sort()
    codesDict = {}
    for c in codes:
        if c in code_mapper:
            codesDict[c] = code_mapper[c]
            del code_mapper[c]
        else:
            codesDict[c] = c
    f.write(";\nclassCodes = " + json.dumps(codesDict) + ";")

    f.write(";\ninstructors = " + json.dumps(obj.culpa_links) + ";")

    f.close()

    # some debug output
    print(code_mapper)
