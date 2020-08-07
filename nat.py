#Converts ASA Nat configuration to Palo NAT configuration
'''
need a function to pull required objects from nat objects.  possibly import from objects.py
once created there.  8-7-20 objects.py not created.  Will likely need to reuse that  function
for other modules.


'''


import re
from ciscoconfparse import CiscoConfParse

filename = "./Configurations/ASA.txt"
converted_filename = "./Configurations/Converted/convertedNat.txt"
STATIC_NAT_REGEX = r'(nat\s\()(\w*)([,])(\w*)(\)\s\w*\s)(static\s)'

class NatConversion():
  def __init__(self, filename=filename, converted_filename=converted_filename):
    self.nat_index = 1
    self.filename = filename
    self.converted_filename = converted_filename
    self.static_nats = self.get_nat(filename, STATIC_NAT_REGEX)

  def increment_index(self):
    self.nat_index = self.nat_index + 1

  def convert_all_nat(self):
    self.create_file()
    self.create_nat_header()
    self.create_rules_header()
    self.palo_static_nat()
    self.create_rules_footer()
    self.create_nat_footer()

  def get_nat (self, file=filename, text=STATIC_NAT_REGEX):
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

  def create_file(self, filename=converted_filename):
    with open(filename, 'w'):
      return

  #CREATE HEADERS
  def create_nat_header(self):
    with open(self.converted_filename, 'a') as f:
      f.write('\t\t\t\t\t\tnat {\n')

  def create_nat_footer(self):
    with open(self.converted_filename, 'a') as f:
      f.write('\t\t\t\t\t\t}\n')

  def create_rules_header(self):
    with open(self.converted_filename, 'a') as f:
      f.write('\t\t\t\t\t\t\trules {\n')

  def create_rules_footer(self):
    with open(self.converted_filename, 'a') as f:
      f.write('\t\t\t\t\t\t\t}\n')

  def palo_static_nat(self):
    if (self.static_nats):
      for s_nat in self.static_nats:
        for line in s_nat:
          self.convert_static_nat(line)
          self.increment_index()
      return
    else:
      return 

  def convert_static_nat(self, nat):
    with open(converted_filename, 'a') as f:
      f.write(str(self.nat_index) + '\n')
    return

   





#main conversion function



#STATIC NAT FUNCTIONS
#BEGIN
#-------------------------------------------------------


if __name__ == '__main__':
  
  Convert = NatConversion()
  Convert.convert_all_nat()