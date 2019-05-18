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
        self.tmp_id = 1

    def add_course(self, num, title, scheduled, points="", prereq_full=""):
        num = num.replace("\u00a0", " ")
        if scheduled:
            self.elements['nodes'].append({
                'data': {
                    'id': num,
                    'num': num,
                    'title': title,
                    'scheduled': scheduled,
                    'points': points,
                    'color': '#ABC4AB' if scheduled else 'grey',
                    'prereq_full': prereq_full,
                    'size': 50
                    }
                })
        self.courses[num] = {
            'num': num,
            'title': title,
            'scheduled': scheduled
        }

    def add_prereq(self, pre, num):
        pre = pre.replace("\u00a0", " ")
        num = num.replace("\u00a0", " ")
        c = self.fuzzy_find(pre)
        if not c:
            self.add_course(pre, pre, True)
        elif c['num'] != pre:
            pre = c['num']

        if not self.courses[pre]['scheduled']:
            return

        self.elements['edges'].append({
            'data': {
                'source': pre,
                'target': num
            }
        })

    def parse(self, data):
        # create nodes
        for course in data:
            title = course['title'][0]
            num = course['num'][0]
            points = course['points']

            prereq_full = "".join(course['prereq'])
            print(num + " : " + title)
            self.add_course(num, title, course['scheduled'], points, prereq_full)
            
        # create edges
        for course in data:
            num = course['num'][0]
            prereq = self.retrieve_prereqs(course['prereq'])
            if course['scheduled']:
                for pre in prereq:
                    if type(pre) == list:
                        for p in pre:
                            self.add_prereq(p, num)
                    else:
                        self.add_prereq(pre, num)
                
        return self.elements

    # some courses don't match exact characters. Try to find them
    def fuzzy_find(self, num):
        if num in self.courses:
            return self.courses[num]
        for c in self.courses.keys():
            if num in c:
                return self.courses[c]
        return None

    PREREQ_PATTERN = re.compile(r'([A-Z]{4} [A-Z][0-9]{4}|[A-Z][0-9]{4}|[oO][rR]|[aA][nN][dD])')

    @staticmethod
    def retrieve_prereqs(prereq_list):
        matches = Converter.PREREQ_PATTERN.findall("".join(prereq_list))

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
    f = open('data/result.json', 'r')
    data = json.loads(f.read())
    f.close()

    obj = Converter()
    elements = obj.parse(data)

    f = open('data/cs-data.js', 'w')
    f.write("elements = ")
    f.write(json.dumps(elements))
    f.write(";\ngenerationDate = '" + datetime.datetime.now().strftime("%m/%d/%Y") + "';")
    f.close()
