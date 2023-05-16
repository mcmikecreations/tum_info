parsed_curriculums = [
  { 'level': 'MSc', 'school': 'CIT', 'name': 'Informatics', 'start': '2023SS', 'end': '2023SS', 'path': 'informatics-ss23.html' },
  { 'level': 'MSc', 'school': 'CIT', 'name': 'Informatics', 'start': '2018SS', 'end': '2023SS', 'path': 'informatics-all.html' },
  { 'level': 'MSc', 'school': 'CIT', 'name': 'DEA', 'start': '2023SS', 'end': '2023SS', 'path': 'dea-ss23.html' },
  { 'level': 'MSc', 'school': 'CIT', 'name': 'DEA', 'start': '2018SS', 'end': '2023SS', 'path': 'dea-all.html' },
]

import sys
import os
import os.path
from bs4 import BeautifulSoup

def process_string(elem):
  return elem.strip().replace('\r', '').replace('\n', '')

def process_term(elem):
  if elem.startswith('?'):
    return ''
  else:
    return '"20{}{}"'.format(elem[2:4], elem[0:2])

def logger(message):
  print(message)

def main():
  if not os.path.isdir('vendor/offered'):
    message = 'Submodules not cloned. Use git submodule init && git submodule update.'
    logger(message)
    exit(1)
  
  current_path = os.path.dirname(os.path.realpath(__file__))
  parent_path = os.path.dirname(current_path)
  offered_path = '{}/vendor/offered'.format(parent_path)

  for curr in parsed_curriculums:
    curr_file = '{}/{}'.format(offered_path, curr['path'])
    with open(curr_file, "rb") as f: soup = BeautifulSoup(f, 'html.parser')

    title = process_string(soup.find('h1').string)
    logger('Parsing {}.'.format(title))

    modules_list = soup.find_all('h3')
    logger('Found {} modules.'.format(len(modules_list)))

    modules = []
    for module in modules_list:
      header = process_string(module.string)
      course_table = next(filter(lambda x: x.name == 'table', module.next_siblings), None)

      course_headers = map(lambda x: process_string(x.string), course_table.find('thead').find('tr').find_all('th'))
      has_theo = 'THEO' in course_headers
      has_last = 'Last offered' in course_headers

      course_list = course_table.find('tbody').find_all('tr')
      # logger('Found {} courses.'.format(len(course_list)))

      courses = []
      for course in course_list:
        items = list(course.find_all('td'))
        course_id = items[0].string
        course_title_elem = items[1].find('a')
        course_title_link = '"{}"'.format(course_title_elem['href']) if course_title_elem else ''
        course_title = items[1].string
        course_credits = items[2].string or ''
        course_theo = ('true' if items[3].string == 'THEO' else 'false') if has_theo else ''
        course_last = process_term(items[-1].string) if has_last else ''

        courses += ['''
    - 
      code: "{}"
      name: "{}"
      url: {}
      credits: {}
      theo: {}
      last: {}'''.format(course_id, course_title.replace('"', '\\"'), course_title_link, course_credits, course_theo, course_last)]

      modules += ['''
  - 
    name: "{}"
    courses:{}'''.format(header.replace('"', '\\"'), ''.join(courses))]
    
    body = '''---
layout: module

school: "{}"
level: "{}"
name: "{}"
semester:
  start: "{}"
  end: "{}"

title: "{}"
modules:{}

---


'''.format(curr['school'], curr['level'], curr['name'], curr['start'], curr['end'], title, ''.join(modules))

    path_dir = '_modules/{}/{}'.format(curr['level'], curr['school'])
    if not os.path.isdir(path_dir):
      os.makedirs(path_dir, exist_ok = True)
    path_file = '{}/{}-{}-{}.md'.format(path_dir, curr['name'], curr['start'][2:6], curr['end'][2:6])
    with open(path_file, 'w') as f:
      f.write(body)
      logger('Wrote {}.'.format(title))

if __name__ == "__main__":
    main()
