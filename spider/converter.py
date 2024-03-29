# This script converts crawled results into a json data file used by the website frontend to show all available info
import argparse
import datetime
import re
import json
import os

# Converter for one semester data
from helpers import get_semester_by_filename


def lazy_read_json(filename: str):
    """
    Source code copied from https://github.com/soid/peqod/blob/5ded73e179c2092f80e1cd9955bcf3ec6773048d/catalog/courses/utils.py

    :return generator returning (json_obj, pos, lenth)

    >>> test_objs = [{'a': 11, 'b': 22, 'c': {'abc': 'z', 'zzz': {}}}, \
                {'a': 31, 'b': 42, 'c': [{'abc': 'z', 'zzz': {}}]}, \
                {'a': 55, 'b': 66, 'c': [{'abc': 'z'}, {'z': 3}, {'y': 3}]}, \
                {'a': 71, 'b': 62, 'c': 63}]
    >>> json_str = json.dumps(test_objs, indent=4, sort_keys=True)
    >>> _create_file("/tmp/test.json", [json_str])
    >>> g = lazy_read_json("/tmp/test.json")
    >>> next(g)
    ({'a': 11, 'b': 22, 'c': {'abc': 'z', 'zzz': {}}}, 120, 116)
    >>> next(g)
    ({'a': 31, 'b': 42, 'c': [{'abc': 'z', 'zzz': {}}]}, 274, 152)
    >>> next(g)
    ({'a': 55, 'b': 66, 'c': [{'abc': 'z'}, {'z': 3}, {'y': 3}]}, 505, 229)
    >>> next(g)
    ({'a': 71, 'b': 62, 'c': 63}, 567, 62)
    >>> next(g)
    Traceback (most recent call last):
      ...
    StopIteration
    """
    with open(filename) as fh:
        state = 0
        json_str = ''
        cb_depth = 0  # curly brace depth
        line = fh.readline()
        while line:
            if line[-1] == "\n":
                line = line[:-1]
            line_strip = line.strip()
            if state == 0 and line == '[':
                state = 1
                pos = fh.tell()
            elif state == 1 and line_strip == '{':
                state = 2
                json_str += line + "\n"
            elif state == 2:
                if len(line_strip) > 0 and line_strip[-1] == '{':  # count nested objects
                    cb_depth += 1

                json_str += line + "\n"
                if cb_depth == 0 and (line_strip == '},' or line_strip == '}'):
                    # end of parsing an object
                    if json_str[-2:] == ",\n":
                        json_str = json_str[:-2]  # remove trailing comma
                    state = 1
                    obj = json.loads(json_str)
                    yield obj, pos, len(json_str)
                    pos = fh.tell()
                    json_str = ""
                elif line_strip == '}' or line_strip == '},':
                    cb_depth -= 1

            line = fh.readline()



class Converter:
    courseNumPattern = re.compile(r'^\w')

    @staticmethod
    def get_data(cu_data_path: str, file: str):
        data = []
        for row, _, _ in lazy_read_json(cu_data_path + "/classes/" + file):
            data.append(row)
        return data

    @staticmethod
    def get_data_files(cu_data_path: str):
        files = [x for x in os.listdir(cu_data_path + "/classes") if x.endswith(".json")]
        files.sort()
        return files

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
        if course['course_code'] in self.courses:
            # merge
            dup_course = self.courses[course['course_code']]
            if course['instructor']:
                if course['instructor'] not in dup_course['instructors']:
                    dup_course['instructors'].append(course['instructor'])
            return

        self.codes.add(course['department_code'])
        if 'instructors' not in course:
            course['instructors'] = []
        if course['instructor'] and course['instructor'] not in course['instructors']:
            course['instructors'].append(course['instructor'])

        # remove not important fields
        important_fields = ['course_code', 'course_title', 'course_descr', 'call_number', 'course_subtitle',
                            'department_code', 'points', 'prerequisites', 'scheduled_days', 'instructors']
        nu_course = {}
        for k in course.keys():
            if k in important_fields:
                nu_course[k] = course[k]

        data = {
            # crawled
            **nu_course,
            # derived
            **{
                'id': course['course_code'],
                # 'color': '#ABC4AB' if course['scheduled'] else 'grey',
                'color': '#ABC4AB',
                'size': 50,
            }
        }

        self.elements['nodes'].append({
            'data': data
        })
        self.courses[course['course_code']] = course

    def add_prereq(self, pre, num, code):
        pre = pre
        c = self.fuzzy_find(pre)
        if not c:
            # class is not listed
            return
        elif c['course_code'] != pre:
            pre = c['course_code']

        if pre == num:
            return

        nu = {
            'data': {
                'source': pre,
                'target': num,
                'code': code
            }
        }
        if nu not in self.elements['edges']:
            self.elements['edges'].append(nu)

    def parse(self, data):
        # create instructors index
        link_re = re.compile(r'/(\d+)$')
        courses = []
        culpa_courses = {}
        for entry in data:
            courses.append(entry)
            if 'instructor_culpa_link' in entry and entry['instructor_culpa_link']:
                self.add_prof_info(entry['instructor'],
                                   count=entry['instructor_culpa_reviews_count'],
                                   culpa_id=link_re.search(entry["instructor_culpa_link"]).group(1))
                if 'instructor_culpa_nugget' in entry:
                    self.culpa_links[entry['instructor']]['nugget'] = entry['instructor_culpa_nugget']
            if entry['instructor_wikipedia_link']:
                self.add_prof_info(entry['instructor'],
                                   wiki=entry["instructor_wikipedia_link"]
                                            .replace("https://en.wikipedia.org/wiki/", "")
                                            .replace(" ", "_"))
            # TODO
            # if entry['type'] == 'culpa_course_link':
            #     culpa_courses[entry['class']] = {
            #         'count': entry['count'],
            #         'id': link_re.search(entry["link"]).group(1)
            #     }
            # TODO
            # if entry['type'] == 'classes_group':
            #     self.add_classes_group(entry['classes-group'], entry['nums'])

        # create nodes
        for course in courses:
            # if course['course_code'] in culpa_courses:
            #     course['culpa'] = culpa_courses[course['course_code']]
            self.add_course(course)
            
        # create edges
        for course in courses:
            course_code = course['course_code']
            prereq = course['prerequisites']
            for pre in prereq:
                if type(pre) == list:
                    for p in pre:
                        self.add_prereq(p, course_code, course['department_code'])
                else:
                    self.add_prereq(pre, course_code, course['department_code'])
                
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

    def __init__(self, cu_data_path, match):
        self.semesters = {}
        self.cu_data_path = cu_data_path
        self.match = match

    def process(self):
        files = Converter.get_data_files(self.cu_data_path)
        for data_file in files:
            if self.match and self.match not in data_file:
                continue
            print("Processing data for:", data_file)
            self._process_file(data_file)
        self._process_semesters_file()

    def _process_file(self, file):
        data = Converter.get_data(self.cu_data_path, file)

        semester_name = get_semester_by_filename(file)
        obj = Converter(semester_name)
        elements = obj.parse(data)

        # store
        filename = semester_name.replace(" ", "-")
        self.semesters[semester_name] = filename
        print(filename)

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

    def _process_semesters_file(self):
        f = open('data/semesters.js', 'w')
        f.write("semesters = ")
        f.write(json.dumps(self.semesters))
        f.write(";\n")
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Columbia catalog data')
    parser.add_argument('cu_data_path', metavar='DATA_PATH', type=str,
                        help='path to CU catalog')
    parser.add_argument('--match',
                        dest="match", type=str,
                        help='Allow only files matching string e.g. 2020-Fall')
    args = parser.parse_args()

    obj = AllSemestersConverter(args.cu_data_path, args.match)
    obj.process()
