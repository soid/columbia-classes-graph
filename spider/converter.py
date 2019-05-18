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

    def add_course(self, num, title, scheduled, points="", prereq_full=""):
        if scheduled:
            self.elements['nodes'].append({
                'data': {
                    'id': num,
                    'title': title,
                    'scheduled': scheduled,
                    'points': points,
                    'color': '#ABC4AB' if scheduled else 'grey',
                    'prereq_full': prereq_full
                    }
                })
        self.courses[num] = {
            'num': num,
            'title': title,
            'scheduled': scheduled
        }

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
            prereq = []
            # TODO: separate AND / OR
            if len(course['prereq'])>0 and course['prereq'][0] == 'Prerequisites: (':
                for p in course['prereq'][1:]:
                    if Converter.courseNumPattern.match(p):
                        prereq.append(p)
            if course['scheduled']:
                for pre in prereq:
                    c = self.fuzzy_find(pre)
                    if not c:
                        self.add_course(pre, pre, True)
                    elif c['num'] != pre:
                        pre = c['num']

                    
                    if not self.courses[pre]['scheduled']:
                        continue

                    self.elements['edges'].append({
                        'data': {
                            'source': pre,
                            'target': num
                        }
                    })
                
        return self.elements

    # some courses don't match exact characters. Try to find them
    def fuzzy_find(self, num):
        if num in self.courses:
            return self.courses[num]
        for c in self.courses.keys():
            if num in c:
                return self.courses[c]
        return None


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
