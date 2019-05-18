import re
import json



class Converter:
    courseNumPattern = re.compile(r'^\w')
    
    def __init__(self):
        self.elements = {}
        self.elements['nodes'] = []
        self.elements['edges'] = []

        self.courses = {}


    def addCourse(self, num, title, scheduled):
        if scheduled:
            self.elements['nodes'].append({
                'data': {
                    'id': num,
                    'title': title,
                    'scheduled': scheduled,
                    'color': 'black' if scheduled else 'grey',
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
            # TODO: separate AND / OR
            # TODO: put full description if it's text
            if len(course['prereq'])>0 and course['prereq'][0] == 'Prerequisites: (':
                for p in course['prereq'][1:]:
                    if Converter.courseNumPattern.match(p):
                        prereq.append(p)

            
            print(num + " : " + title + " : " + str(prereq))
            self.addCourse(num, title, course['scheduled'])
            
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

f = open('spider/result.json', 'r')
data = json.loads(f.read())
f.close()

obj = Converter()
elements = obj.parse(data)

f = open('cs-data.js', 'w')
f.write("elements = ")
f.write(json.dumps(elements))
f.close()
                
