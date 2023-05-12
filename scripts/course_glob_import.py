import sys
import os
import course_functions
import json

def logger(message):
  print(message)

args = sys.argv
if ('-h' in args or
    len(args) < 2):
  logger('''scripts/course_glob_import.py <filepath> [-h -v]
<filepath> Path to the json text file with grades extracted through the UI.
-h Print this help message.
-v Verbose output.
Check script source if a school mapping is missing.
If unsure about abbreviation, check tum.de subdomain.
''')
  exit(0)

filename = args[1]
verbose = len(list(filter(lambda x: x.startswith('-v'),args))) > 0

with open(filename, 'r') as file_object:
  achievements = json.load(file_object)

achievements = list(filter(
  lambda x: course_functions.achievement_exists(x, logger, verbose) == False,
  achievements))
logger('Performing grade stats save...')
achievements = list(map(lambda x: course_functions.achievement_save(x, logger, verbose), achievements))
logger('Finished.')