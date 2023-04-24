# TODO: if script complains, update this dict and rerun
schools = {
  'IN': 'CIT',
  'MA': 'CIT',
  'EI': 'CIT',
  'WI': 'MGT',
  'SZ': 'SZ',
  'MW': 'ED',
  'BV': 'ED',
  'CLA': 'SOT',
  'ED': 'SOT',
  'SOT': 'SOT',
  'MCTS': 'MCTS',
  'POL': 'MCTS',
  'ME': 'MED',
  'PH': 'NAT',
}
ects = {
  0.0: 1,
  0.5: 1,
  1.0: 2,
  1.5: 3,
  2.0: 3,
  3.0: 4,
  4.0: 5,
  5.0: 7,
  6.0: 8,
  7.0: 9,
  9.0: 10,
}

from bs4 import BeautifulSoup
import sys
import re
import os
import os.path

args = sys.argv
soup = None

with open(args[1]) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

courses = soup.find_all('h3')
print('Found {} courses.'.format(len(courses)))

def process_achievement(course):
  achievement = dict()
  header = course.string.strip().replace('\r', '').replace('\n', '')
  header_regex = r"^([0-9\-]+) - ([\w-]+) (.+) \(([\d.]+)SWS .+ ([WS])S 20(\d+)/(\d+)\)$"
  header_match = re.search(header_regex, header)
  if header_match == None:
    raise Exception(header)
  header_number = header_match.group(2)
  header_number_regex = r"^([A-Z]+).+$"
  header_dep = re.search(header_number_regex, header_number).group(1)
  header_school = None
  if header_dep in schools:
    header_school = schools[header_dep]
  else:
    raise Exception('Unknown course dep: {}'.format(header_dep))
  header_sem = header_match.group(6) if header_match.group(5) == 'W' else header_match.group(7)
  header_hours = float(header_match.group(4))
  header_ects = 0
  if header_hours not in ects:
    raise Exception('Unknown SWS: {}'.format(header_hours))

  achievement = {
    'id': 0,
    'href': '',
    'mode': 'written',
    'date': '{} 12:00:00 +0100'.format(header_match.group(1)),
    'number': header_number,
    'name': header_match.group(3),
    'type': 'endterm',
    'semester': '20{}S'.format(header_sem + header_match.group(5)),
    'hours': header_hours,
    'ects': ects[header_hours],
    'school': header_school,
  }

  grade_elem = next(filter(lambda x: x.name == 'div', course.next_siblings), None)
  grade_list = grade_elem.find_all('div', class_='kandcountbox')
  
  achievement = process_grades(achievement, grade_list)
  return achievement
  
def process_grades(achievement, grade_list):
  grades = dict()
  for grade_elem in grade_list:
    grade_people_elem = next(filter(lambda x: x.name == 'div', grade_elem.next_siblings), None)
    grade_people_text = grade_people_elem.contents[-1].strip()
    grade_people_regex = r"^(\d+) K.$"
    grade_people = int(re.search(grade_people_regex, grade_people_text).group(1))
    if grade_people == 0:
      continue

    grade_value_elem = next(filter(lambda x: x.name == 'div', grade_people_elem.next_siblings), None)
    grade_value_text = grade_value_elem.div.contents[-1].strip()
    grade_value = 0.0
    # X didn't show up
    # U cheated
    # Q withdrew
    # Z rejected
    # B passed without grade
    # N didn't pass without grade
    if 'X' in grade_value_text:
      grade_value = 6.0
    elif 'U' in grade_value_text:
      grade_value = 5.0
      achievement['cheated'] = grade_people
    elif 'Z' in grade_value_text:
      grade_value = 5.0
      achievement['rejected'] = grade_people
    elif 'Q' in grade_value_text:
      achievement['withdrew'] = grade_people
      continue
    elif 'B' in grade_value_text:
      continue
    else:
      try:
        grade_value = float(grade_value_text.replace(',', '.'))
      except:
        print('Failed to parse {}. Contact mcmikecreations.'.format(grade_value_text))
        achievement['grades'] = None
        return achievement
    
    grades[grade_value] = {
        'value': grade_value,
        'count': grade_people,
      }

  achievement['grades'] = list(grades.values())
  achievement['grades'].sort(key=lambda x: x['value'])
  return achievement

# Check if an achievement exists; if not, create the dir as a side-effect
def achievement_exists(achievement):
  path_dir = '_courses/{}/{}'.format(achievement['school'], achievement['number'])
  path_file = '{}/{}-{}.md'.format(path_dir, achievement['semester'], achievement['type'])
  if os.path.isdir(path_dir):
    if os.path.isfile(path_file):
      print('{} {} {} exists. Check endterm/retake. If wrong, add manually.'.format(
        achievement['number'], achievement['name'], achievement['type']))
      return True
    return False
  os.makedirs(path_dir, exist_ok = True)
  return False

def achievement_save(achievement):
  path_dir = '_courses/{}/{}'.format(achievement['school'], achievement['number'])
  path_file = '{}/{}-{}.md'.format(path_dir, achievement['semester'], achievement['type'])
  text_grades = list(map(lambda x: '  - {{ grade: {0}, people: {1} }}\n'.format(x['value'], x['count']), achievement['grades']))
  text_desc = ''
  if 'cheated' in achievement:
    text_desc += '{} people cheated. Added to 5.0 column. '.format(achievement['cheated'])
  if 'withdrew' in achievement:
    text_desc += '{} people withdrew. Not present on the plot. '.format(achievement['withdrew'])
  if 'rejected' in achievement:
    text_desc += '{} people rejected. Added to 5.0 column. '.format(achievement['rejected'])
  text_file = '''---
layout: course

school: "{school}"
code: "{number}"
semester: "{semester}" # refers to the year of the semester start
exam_type: "{type}"
name: "{name}"
date: "{date}"

ects: {ects}
hours: {hours} # semester hours
mode: "{mode}"
lang: "en"

title: "{name} {semester} {type_cap}"
grades:
{grades}
---

{desc}
'''.format(school=achievement['school'], number=achievement['number'].upper(),
    semester=achievement['semester'], type=achievement['type'],
    name=achievement['name'], date=achievement['date'],
    ects=achievement['ects'], hours=achievement['hours'],
    mode=achievement['mode'], type_cap=achievement['type'].capitalize(),
    grades=''.join(text_grades), desc=text_desc)
  
  with open(path_file, 'w') as f:
    f.write(text_file)
    print('Wrote {} {} {}. Check endterm/retake filename and field in file. Check exam_type, mode, lang fields in file.'.format(
      achievement['number'], achievement['name'], achievement['type']))
  return achievement

for course in courses:
  achievement = process_achievement(course)
  if achievement['grades'] == None or achievement_exists(achievement):
    continue
  achievement_save(achievement)
