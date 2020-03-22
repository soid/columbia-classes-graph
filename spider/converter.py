# This script converts crawled results into a json data file used by the website frontend to show all available info

import datetime
import re
import json
from os.path import dirname, isfile, realpath
import os

from allclasses import ClassesSpider


# Converter for one semester data
from helpers import sort_semesters, get_semester_by_filename


class Converter:
    courseNumPattern = re.compile(r'^\w')

    @staticmethod
    def get_data(file):
        with open(Converter.get_data_dir() + file, 'r') as file:
            return json.loads(file.read())

    @staticmethod
    def get_data_files():
        files = [x for x in os.listdir(Converter.get_data_dir()) if x.startswith("data-")]
        return files

    @staticmethod
    def get_data_dir():
        return dirname(dirname(realpath(__file__))) + '/data/'

    """Load parsed data from file"""
    def __init__(self, semester):
        self.semester = semester
        self.elements = {}
        self.elements['nodes'] = []
        self.elements['edges'] = []

        self.courses = {}
        self.culpa_links = {}
        self.codes = set()
        self.class_groups = {}
        self.tmp_id = 1
        self.semesters = {}

    def add_course(self, course):
        course['num'] = course['num']
        for semester in course['schedule'].keys():
            self.semesters[semester] = True
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
        link_re = re.compile(r'/(\d+)$')
        courses = []
        culpa_courses = {}
        for entry in data:
            if entry['type'] == 'class':
                if self.semester not in entry['schedule'].keys():
                    # skip if not this semester
                    continue
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
            if entry['type'] == 'classes_group':
                self.add_classes_group(entry['classes-group'], entry['nums'])

        # create nodes
        for course in courses:
            if course['num'] in culpa_courses:
                course['culpa'] = culpa_courses[course['num']]
            title = course['title']
            num = course['num']
            # print(num + " : " + title)
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

    # some classes are grouped no by the class code, but by other means, e.g. the Core
    def add_classes_group(self, group_name, nums):
        self.class_groups[group_name] = nums

    def get_semesters(self):
        return sort_semesters(self.semesters.keys())

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


class AllSemestersConverter:

    def process(self):
        files = Converter.get_data_files()
        for data_file in files:
            print("Processing data for:", data_file)
            self._process_file(data_file)

    def _process_file(self, file):
        data = Converter.get_data(file)

        obj = Converter(get_semester_by_filename(file))
        elements = obj.parse(data)
        filename = obj.get_semesters()[-1]
        filename = filename.replace(" ", "-")

        # write output
        f = open('data/classes-' + filename + '.js', 'w')
        f.write("elements = ")
        f.write(json.dumps(elements))
        f.write(";\ngenerationDate = '" + datetime.datetime.now().strftime("%m/%d/%Y") + "';\n")

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
        f.write("classCodes = " + json.dumps(codesDict) + ";\n")

        groupsDict = {}
        for group_name in obj.class_groups.keys():
            groupsDict[group_name] = obj.class_groups[group_name]
        f.write("classGroups = " + json.dumps(groupsDict) + ";\n")

        f.write("instructors = " + json.dumps(obj.culpa_links) + ";\n")

        f.close()

        # some debug output
        # print(code_mapper)


if __name__ == "__main__":
    obj = AllSemestersConverter()
    obj.process()
