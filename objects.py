# Takes ASA objects and coverts them into Palo Objects.  Eventually will create
# an excel showing mappings.

'''
Should create a function to pass to other modules that will pull required objects
for that specific module.  Ie nat.py/access_policy.py will also require ect..
'''

import re
from ciscoconfparse import CiscoConfParse

#temporary.  filename / converted filename will be passed as arguements from main.py once created
#can keepp file/converted filename as defaults but will need to create a function that will
#make the required dirs.
filename = "./Configurations/ASA.txt"
converted_filename = "./Configurations/Converted/convertedObjects.txt"
object_regex = r''#need a regex to match all objects

def find_objects (file=filename, text=object_regex):
  '''
  Returns interfaces as parent objects from ASA config.
  Takes two arguments(ASACONFIG, SEARCHSTRING).
  '''
  parent = []
  parse = CiscoConfParse(file)
  for obj in parse.find_objects(text):
    each_obj = []
    each_obj.append(obj.text)
    for each in obj.all_children:
      each_obj.append(each.text)
    parent.append(each_obj)
  return parent