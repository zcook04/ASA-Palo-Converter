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
FILENAME = "./Configurations/ASA.txt"
CONVERTED_FILENAME = "./Configurations/Converted/convertedObjects.txt"

SEARCH_NETWORK_O = r'(object\s)(network\s)([A-Za-z-_\d.]*)'
SEARCH_NETWORK_G = r'(object-group\s)(network\s)([A-Za-z-_\d.]*)'
SEARCH_SERVICE_O = r'(object\s)(service\s)([A-Za-z-_\d.]*)'
SEARCH_SERVICE_G = r'(object-group\s)(service\s)([A-Za-z-_\d.]*)'

class Objects():
  def __init__(self, FILENAME, search_text):
    self.objects = self.find_objects(FILENAME, search_text)
  
  def find_objects (self, file, search_text):
    '''
    Returns interfaces as parent objects from ASA config.
    Takes two arguments(ASACONFIG, SEARCHSTRING).
    '''
    parent = []
    parse = CiscoConfParse(file)
    for obj in parse.find_objects(search_text):
      each_obj = []
      each_obj.append(obj.text)
      for each in obj.all_children:
        each_obj.append(each.text)
      parent.append(each_obj)
    return parent

  def filter_obj_types(self, filter):
    filtered_objs = []
    for obj in self.objects:
      for lines in obj:
        if(re.search(filter, lines) != None):
          filtered_objs.append(obj)
    return filtered_objs

class Network(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_NETWORK_O)

  def get_host_objs(self):
    filter = r'(host\s\d*[.]\d*[.]\d*[.]\d*)'
    return self.filter_obj_types(filter)

  def get_subnet_objs(self):
    filter = r'(subnet\s\d*[.]\d*[.]\d*[.]\d*)'
    return self.filter_obj_types(filter)

  def get_fqdn_objs(self):
    filter = r'(fqdn\s\w+)'
    return self.filter_obj_types(filter)

  def get_nat_objs(self):
    filter = r'(nat\s)(\()(\w+)[,](\w+)'
    return self.filter_obj_types(filter)

class NetworkGroup(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_NETWORK_G)

class Service(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_SERVICE_O)
    pass

class ServiceGroup(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_SERVICE_G)
    pass

if __name__ == '__main__':
  #Create Python Objects for ASA Objects
  NetworkObjects = Network()
  NetworkGroupObjects = NetworkGroup()
  ServiceObjects = Service()
  ServiceGroupObjects = ServiceGroup()

  #testing ------BELOW---------
  network_hosts = NetworkObjects.get_host_objs()
  network_subnets = NetworkObjects.get_subnet_objs()
  network_nat = NetworkObjects.get_nat_objs()
  print(network_nat)