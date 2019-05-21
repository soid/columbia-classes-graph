import datetime
import re
import json


class Converter:
    courseNumPattern = re.compile(r'^\w')
    
    def __init__(self):
        self.elements = {}
        self.elements['nodes'] = []
        self.elements['edges'] = []

        self.courses = {}
        self.codes = set()
        self.tmp_id = 1

    def add_course(self, course):
        course['num'] = course['num']
        if course['scheduled']:
            self.codes.add(course['code'])
            self.elements['nodes'].append({
                'data': {
                    # crawled
                    **course,
                    # derived
                    **{
                        'id': course['num'],
                        'color': '#ABC4AB' if course['scheduled'] else 'grey',
                        'size': 50,
                    }
                }
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

        self.elements['edges'].append({
            'data': {
                'source': pre,
                'target': num,
                'code': code
            }
        })

    def parse(self, data):
        # create nodes
        for course in data:
            title = course['title']
            num = course['num']
            print(num + " : " + title)
            self.add_course(course)
            
        # create edges
        for course in data:
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

    # some courses don't match exact characters. Try to find them
    def fuzzy_find(self, num):
        if num in self.courses:
            return self.courses[num]
        for c in self.courses.keys():
            if num in c:
                return self.courses[c]
        return None

    PREREQ_PATTERN = re.compile(r'([A-Z]{4} [A-Z][A-Z]?[0-9]{4}|[A-Z][A-Z]?[0-9]{4}|[oO][rR]|[aA][nN][dD])')

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
    f = open('data/all-classes.json', 'r')
    data = json.loads(f.read())
    f.close()

    obj = Converter()
    elements = obj.parse(data)

    f = open('data/classes-data.js', 'w')
    f.write("elements = ")
    f.write(json.dumps(elements))
    f.write(";\ngenerationDate = '" + datetime.datetime.now().strftime("%m/%d/%Y") + "';")

    # generate a list of all codes
    codes = list(obj.codes)
    codes.sort()
    codesDict = {}
    for c in codes:
        if c == "COMS":
            codesDict[c] = "Computer Science"
        else:
            codesDict[c] = c
    f.write(";\nclassCodes = " + json.dumps(codesDict) + ";")

    f.close()
