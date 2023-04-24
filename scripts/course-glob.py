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

import sys

args = sys.argv
list_name = list(filter(lambda x: x.startswith('name='),args))
list_pass = list(filter(lambda x: x.startswith('pass='),args))
if ('-h' in args or
    len(list_name) == 0 or
    len(list_pass) == 0):
  print('''scripts/course-glob.py name=ab12cde@mytum.de pass=42424242 [-h -v]
name=<> Verbatim TUMOnline login name. Can be email or whatever it accepts.
pass=<> Password corresponding to the name.
-h Print this help message.
-v Verbose output.
Check script source if a school mapping is missing.
If unsure about abbreviation, check tum.de subdomain.
''')
  exit(0)

user_name = list_name[0][5:]
user_pass = list_pass[0][5:]
verbose = len(list(filter(lambda x: x.startswith('-v'),args))) > 0

# This script does:
# - acquire a temporary session id and access token to load your data
# - load a list of your achievements to extract statistics
# - load each achievement to extract course properties
# - load exam statistics for each exam to extract the grade distribution
# - save exam statistics to disk
# This script does not:
# - send your login/password/session/token anywhere outside TUMOnline
# - store your personal data anywhere, apart from the info gathered for the website
#   **Note**: your info remains on your machine until you commit and push the changes
# - expose sensitive data or print it in full form anywhere outside the python environment
#   **Warn**: verbose output option would partially show ids and tokens
# - expose achievement data outside the python environment and the host (terminal/pipe)

# Check working directory
import os
import os.path

if os.path.isfile('./scripts/course-glob.py') == False:
  print('Wrong working directory. Execute from repository root.')
  exit(1)

print('Found correct working directory.')

class AuthModel:
  def __init__(self, cookie, token):
    self.cookie = cookie
    self.token = token

import requests # for http communication
from urllib.parse import urlparse, parse_qs # for redirect url parsing
from datetime import datetime # for achievement date parsing
import re # for course number parsing

# Perform initial login into the system
def perform_login(username, password):
  # First get session cookie for next requests.
  head_session = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'Host': 'campus.tum.de',
    'Referer': 'https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
  }
  res_session = requests.get('https://campus.tum.de/tumonline/pl/ui/$ctx/wbOAuth2.session?language=en',
    headers=head_session)
  if res_session.status_code != 200:
    print('Session cookie: received bad status {}'.format(res_session.status_code))
    exit(1)
  res_session_id = res_session.cookies['PSESSIONID']
  if verbose:
    print('Session cookie: {}...'.format(res_session_id[0:40]))
  
  # Then get authorization endpoint with state wrapper from a separate request.
  head_auth = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'Host': 'campus.tum.de',
    'Origin': 'https://campus.tum.de',
    'Referer': 'https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
  }
  res_auth = requests.post('https://campus.tum.de/tumonline/ee/rest/auth/user',
    headers=head_auth,
    cookies=dict(PSESSIONID=res_session_id))
  if res_auth.status_code != 200:
    print('Auth redirect state: received bad status {}'.format(res_auth.status_code))
    exit(1)
  res_auth_url = urlparse(
    res_auth.json()['resource'][0]['content']['authenticationResponse']['authEndpointUrl']
    .format(username=username, password=password))
  res_auth_dict = parse_qs(res_auth_url.query)
  if verbose:
    print('Auth redirect state: {}...'.format(res_auth_dict['pStateWrapper'][0][0:40]))

  # Now get a redirect to the real login page using the cookie. This also provides a new login cookie.
  res_redirect = requests.post(res_auth_url._replace(query="").geturl(),
    headers=head_auth,
    cookies=dict(PSESSIONID=res_session_id),
    data=res_auth_dict,
    allow_redirects=False)
  if res_redirect.status_code != 302:
    print('Auth redirect url: received bad status {}'.format(res_redirect.status_code))
    exit(1)
  
  res_session_id = res_redirect.cookies['PSESSIONID']
  res_redirect_url = res_redirect.headers.get('location')
  if verbose:
    print('Session cookie: {}...'.format(res_session_id[0:40]))
    print('Auth redirect url: {}...'.format(urlparse(res_redirect_url).query[0:40]))

  # Finally receive access token using the redirect location
  res_token = requests.get(res_redirect_url,
    headers=head_session,
    cookies=dict(PSESSIONID=res_session_id))
  if res_token.status_code != 200:
    print('Auth token: received bad status {}'.format(res_token.status_code))
    exit(1)
  res_token_value = res_token.json()['access_token']
  if verbose:
    print('Auth token: {}...'.format(res_token_value[0:20]))

  return AuthModel(res_session_id, res_token_value)

# Receive a specific profile session and token
def perform_profile(auth):
  # A new set of session id and token is required for profile functions
  head_profile = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'Authorization': 'Bearer {}'.format(auth.token),
    'Host': 'campus.tum.de',
    'Origin': 'https://campus.tum.de',
    'Referer': 'https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
  }
  res_profile = requests.post('https://campus.tum.de/tumonline/ee/rest/auth/profile',
    headers=head_profile,
    cookies=dict(PSESSIONID=auth.cookie),
    data={ 'pProfileKey': 'STUDENT', 'profile_key': 'STUDENT' })
  if res_profile.status_code != 200:
    print('Auth token: received bad status {}'.format(res_profile.status_code))
    exit(1)
  
  res_session_id = res_profile.cookies['PSESSIONID']
  res_token_value = res_profile.json()['accessToken']
  if verbose:
    print('Session cookie: {}...'.format(res_session_id[0:40]))
    print('Auth token: {}...'.format(res_token_value[0:20]))

  return AuthModel(res_session_id, res_token_value)

# Gather and filter all achievements
def perform_achievements(auth):
  head_achieve = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'Authorization': 'Bearer {}'.format(auth.token),
    'Host': 'campus.tum.de',
    'Referer': 'https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
  }
  res_achieve = requests.get('https://campus.tum.de/tumonline/ee/rest/slc.xm.ac/achievements?$orderBy=acDate=descnf',
    cookies=dict(PSESSIONID=auth.cookie),
    headers=head_achieve)
  if res_achieve.status_code != 200:
    print('Achievements: received bad status {}'.format(res_achieve.status_code))
    exit(1)
  res_achieve_list = list(filter(lambda o:
    o['content']['type'] == 'model-slc.xm.ac.achievementDto'
    and o['content']['achievementDto']['achievementType'] == 'EXAM'
    and o['content']['achievementDto']['achievementStatusType'] == 'FINAL',
    res_achieve.json()['resource']))
  if verbose:
    print('Achievements: {} items initial'.format(len(res_achieve_list)))
  
  def mapping(o):
    name = ''
    try:
      name = o['content']['achievementDto']['cpCourseLibDto']['courseTitle']['value']
    except:
      return None
    
    try:
      href = o['link'][0]['href']
      date = datetime.strptime(
        o['content']['achievementDto']['achievementDate']['value'],
        '%Y-%m-%dT%H:%M:%S')
      id = o['content']['achievementDto']['id']
      semester = o['content']['achievementDto']['semesterLibDto']['key']
      hours = o['content']['achievementDto']['cpCourseLibDto']['semesterHours']
      ects = o['content']['achievementDto']['credits']
      course_type = o['content']['achievementDto']['cpCourseLibDto']['courseTypeDto']['key']
      if course_type != 'FA':
        raise Exception('Wrong course type: {}'.format(course_type))
      course_number_regex = r"^([A-Z]+).+$"
      course_number = o['content']['achievementDto']['cpCourseLibDto']['courseNumber']['courseNumber']
      course_dep = re.search(course_number_regex, course_number).group(1)
      if course_dep in schools:
        course_school = schools[course_dep]
      else:
        raise Exception('Unknown course dep: {}'.format(course_dep))
      course_names = o['content']['achievementDto']['cpCourseLibDto']['courseTitle']['translations']['translation']
      name = next(map(lambda y: y['value'], filter(lambda x: x['lang'] == 'en', course_names)), name)
      exam_type = 'endterm'

      return {
        'href': href,
        'id': id,
        'name': name,
        'type': exam_type,
        'date': date.strftime("%Y-%m-%d %H:%M:%S +0100"),
        'semester': '20{}S'.format(semester),
        'hours': hours,
        'ects': ects,
        'school': course_school,
        'number': course_number,
      }
    except Exception as e:
      print('Failed to parse: {}. {}'.format(name, e))
      return None

  res_achieve_list = list(filter(lambda o: o != None, map(mapping, res_achieve_list)))
  if verbose:
    print('Achievements: {} items filtered'.format(len(res_achieve_list)))

  return res_achieve_list

# Load info related to a specific exam attempt
def perform_exam(auth, achievement):
  # Get exam mode (written/oral) and grades url
  head_achieve = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'Authorization': 'Bearer {}'.format(auth.token),
    'Host': 'campus.tum.de',
    'Referer': 'https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
  }
  res_achieve = requests.get('{}?$ctx=design=ca;lang=en'.format(achievement['href']),
    cookies=dict(PSESSIONID=auth.cookie),
    headers=head_achieve)
  if res_achieve.status_code != 200:
    print('Achievement {}: received bad status {}'.format(achievement['id'], res_achieve.status_code))
    exit(1)
  res_achieve_json = res_achieve.json()
  res_achieve_o = res_achieve_json['resource'][0]['content']['achievementExamDto']
  mode = res_achieve_o['examModeType']['name']['value'].lower()
  res_achieve_grades_url = next(map(
    lambda y: y['href'], 
    filter(lambda x: x['name'] == 'examstatisticCourse', res_achieve_json['resource'][0]['link'])
    ), None)
  if res_achieve_grades_url == None:
    print('Achievement {}: failed to find grades url')
    exit(1)
  
  # Get grade list
  res_achieve = requests.get(res_achieve_grades_url,
    cookies=dict(PSESSIONID=auth.cookie),
    headers=head_achieve)
  if res_achieve.status_code != 200:
    print('Achievement {} grade: received bad status {}'.format(achievement['id'], res_achieve.status_code))
    exit(1)
  res_achieve_grades = res_achieve.json()['gradeEntries']
  if len(res_achieve_grades) == 0:
    return None
  
  grades = dict()
  for o in res_achieve_grades:
    value = 0.0
    if 'gradeCommentShortName' in o:
      # X didn't show up
      # U cheated
      # Q withdrew
      # Z rejected
      # B passed without grade
      # N didn't pass without grade
      short_name = o['gradeCommentShortName']
      if short_name == 'X':
        value = 6.0
      elif short_name == 'U':
        if 'cheated' not in achievement:
          achievement['cheated'] = 0
        achievement['cheated'] += 1
        value = 5.0
      elif short_name == 'Z':
        if 'rejected' not in achievement:
          achievement['rejected'] = 0
        achievement['rejected'] += 1
        value = 5.0
      elif short_name == 'Q':
        if 'withdrew' not in achievement:
          achievement['withdrew'] = 0
        achievement['withdrew'] += 1
        continue
      elif short_name == 'B':
        continue
      elif short_name == 'N':
        continue
      else:
        print('TODO: report to mcmikecreations - unknown type {}'.format(short_name))
        continue
    else:
      value = float(o['gradeShortName'].replace(',', '.'))

    if value not in grades:
      grades[value] = {
        'value': value,
        'count': 0,
      }
    
    grades[value]['count'] += 1
  
  achievement['mode'] = mode
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
    name=achievement['name'].replace('"', '\\"'), date=achievement['date'],
    ects=achievement['ects'], hours=achievement['hours'],
    mode=achievement['mode'], type_cap=achievement['type'].capitalize(),
    grades=''.join(text_grades), desc=text_desc)
  
  with open(path_file, 'w') as f:
    f.write(text_file)
    print('Wrote {} {} {}. Check endterm/retake filename and field in file. Check exam_type, mode, lang fields in file.'.format(
      achievement['number'], achievement['name'], achievement['type']))
  return achievement

print('Performing login...')
auth = perform_login(user_name, user_pass)
print('Performing profile lookup...')
auth = perform_profile(auth)
print('Performing achievements lookup...')
achievements = list(filter(lambda x: achievement_exists(x) == False, perform_achievements(auth)))
print('Performing grade stats lookup...')
achievements = list(filter(lambda y: y != None, map(lambda x: perform_exam(auth, x), achievements)))
print('Performing grade stats save...')
achievements = list(map(achievement_save, achievements))
print('Finished.')
