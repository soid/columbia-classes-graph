import re
import json



class Converter:
    courseNumPattern = re.compile(r'^\w')
    
    def __init__(self):
        self.elements = {}
        self.elements['nodes'] = []
        self.elements['edges'] = []

        self.courses = {}


    def addCourse(self, num, title, scheduled, prereq_full=""):
        if scheduled:
            self.elements['nodes'].append({
                'data': {
                    'id': num,
                    'title': title,
                    'scheduled': scheduled,
                    'color': '#ABC4AB' if scheduled else 'grey',
                    'prereq_full': prereq_full
                    }
                })
        self.courses[num] = {
            'title': title,
            'scheduled': scheduled
        }


    def parse(self, data):
        id2course = {}
        for course in data:
            title = course['title'][0]
            num = course['num'][0]
            
            prereq = []
            prereq_full = ""
            # TODO: separate AND / OR
            if len(course['prereq'])>0 and course['prereq'][0] == 'Prerequisites: (':
                prereq_full = "".join(course['prereq'])
                for p in course['prereq'][1:]:
                    if Converter.courseNumPattern.match(p):
                        prereq.append(p)

            
            print(num + " : " + title + " : " + str(prereq))
            self.addCourse(num, title, course['scheduled'], prereq_full)
            
            if course['scheduled']:
                for pre in prereq:
                    if not pre in self.courses:
                        self.addCourse(pre, pre, True)
                    
                    if not self.courses[pre]['scheduled']:
                        continue

                    self.elements['edges'].append({
                        'data': {
                            'source': pre,
                            'target': num
                        }
                    })
                
        return self.elements

f = open('data/result.json', 'r')
data = json.loads(f.read())
f.close()

obj = Converter()
elements = obj.parse(data)

f = open('data/cs-data.js', 'w')
f.write("elements = ")
f.write(json.dumps(elements))
f.close()
                
