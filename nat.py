#Converts ASA Nat configuration to Palo NAT configuration
'''
need a function to pull required objects from nat objects.  possibly import from objects.py
once created there.  8-7-20 objects.py not created.  Will likely need to reuse that  function
for other modules.
'''

import re
from ciscoconfparse import CiscoConfParse
from interfaces import filtered_interfaces #For to-interface mappings
from objects import Network #For object nat

FILENAME = "./Configurations/ASA.txt"
CONVERTED_FILENAME = "./Configurations/Converted/convertedNat.txt"
STATIC_NAT_REGEX = r'(nat\s\()(\w*)([,])(\w*)(\)\s\w*\s)(static\s)'

class NatConversion():
  def __init__(self, FILENAME=FILENAME, CONVERTED_FILENAME=CONVERTED_FILENAME):
    self.nat_index = 1
    self.FILENAME = FILENAME
    self.CONVERTED_FILENAME = CONVERTED_FILENAME
    self.static_nats = self.get_nat(FILENAME, STATIC_NAT_REGEX)

  def palo_static_nat(self):
    if (self.static_nats):
      for s_nat in self.static_nats:
        for line in s_nat:
          self.create_nat_rule_header()
          self.create_static_source_translation()
          self.create_static_ip(line)
          self.close_static_ip()
          self.close_static_source_translation()
          self.set_nat_rule_attributes(line)
          self.create_nat_rule_footer()
          self.increment_index()
      return
    else:
      return

  def increment_index(self):
    self.nat_index = self.nat_index + 1
  
  def tabs(self, num_tabs):
    return '\t'*num_tabs

  def convert_all_nat(self):
    self.create_file()
    self.create_nat_header()
    self.create_rules_header()
    self.palo_static_nat()
    self.create_rules_footer()
    self.create_nat_footer()

  def get_nat (self, asa_conf, search_string):
    '''
    Returns asa config as parent/child config objects.  Filter is
    used to select portions of the configuration. That match the
    filter string.  Takes two arguments (ASACONFIG, SEARCHSTRING).
    '''
    parent = []
    parse = CiscoConfParse(asa_conf)
    for obj in parse.find_objects(search_string):
      each_obj = []
      each_obj.append(obj.text)
      for each in obj.all_children:
        each_obj.append(each.text)
      parent.append(each_obj)
    return parent

  def create_file(self, FILENAME=CONVERTED_FILENAME):
    with open(FILENAME, 'w'):
      return

  #CREATE HEADERS
  def create_nat_header(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}nat {{\n')

  def create_nat_footer(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}}}\n')

  def create_rules_header(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(7)}rules {{\n')

  def create_rules_footer(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(7)}}}\n') 

  def create_nat_rule_header(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(8)}nat_{self.nat_index} {{\n')
    return

  def create_nat_rule_footer(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(8)}}}\n')
    return

  def create_static_source_translation(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}source-translation {{\n')
    return

  def close_static_source_translation(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}}}\n')
    return

  def create_static_ip(self, line):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(10)}static-ip {{\n')
      f.write(f'{self.tabs(11)}{self.static_translated_addr(line)}')
      f.write(f'{self.tabs(11)}bi-directional {self.static_bi_directional(line)}')
    return

  def close_static_ip(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(10)}}}\n')
    return

  def static_translated_addr(self, line):
      line_array = line.split(' ')
      return f'translated-address {line_array[5]};\n'

  def get_static_ip_opts(self, line):
    options = {}
    line_size_no_options = 6
    line_array = line.split(' ')
    if (len(line_array) <= line_size_no_options):
      return options
    if ('destination' in line_array):
      destination = line_array.index('destination')
      options['destination-orig'] = line_array[destination+2]
      options['destination-trans'] = line_array[destination+3]
    if ('description' in line_array):
      description = line_array.index('description')
      options['description'] = ' '.join(line_array[description+1:])
    if ('inactive' in line_array):
      options['disabled'] = 'yes;'
    if ('service' in line_array):
      service = line_array.index('service')
      options['service-orig'] = line_array[service+1]
      options['service-trans'] = line_array[service+2]
    if ('no-proxy-arp' in line_array):
      options['no-proxy-arp'] = True
    if ('unidirectional' in line_array):
      options['unidirectional'] = True
    if ('dns' in line_array):
      options['dns'] = True
    if ('route-lookup' in line_array):
      options['route-lookup'] = True
    return options


  def static_bi_directional(self, line):
    options = self.get_static_ip_opts(line)
    if (options.get('unidirectional') != None):
      return 'no;\n' #needs logic
    return 'yes;\n'

  def static_to_zone(self, line):
    to_search = re.compile(r'(nat\s\()(\w*)([,])(\w*)')
    to_zone = re.search(to_search, line).group(4)
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}to {to_zone};\n')
    return

  def static_from_zone(self, line):
    from_search = re.compile(r'(nat\s\()(\w*)([,])(\w*)')
    from_zone = re.search(from_search, line).group(2)
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}from {from_zone};\n')
    return

  def static_source_obj(self, line):
    line_array = line.split(' ')
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}source {line_array[4]};\n')
    return

  def static_to_interface(self, line):
    search_int_name = r'(nameif\s)(\w*)'
    search_line_name = r'(nat\s)(\(\w*[,])(\w*)'
    for intf in filtered_interfaces:
      s_intf = ' '.join(intf)
      int_name = re.search(search_int_name, s_intf)
      line_name = re.search(search_line_name, line)
      if(int_name.group(2) == line_name.group(3)):
        return(int_name.group(2))
      

  def set_nat_rule_attributes(self, line):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      options = self.get_static_ip_opts(line)
      self.static_to_zone(line)
      self.static_from_zone(line)
      self.static_source_obj(line)
      if ('destination-trans' in options.keys()):
        f.write(f'{self.tabs(9)}destination {options["destination-trans"]}\n')
      else:
        f.write(f'{self.tabs(9)}destination any;\n')
      if ('service' in options.keys()):#Needs reworked
        f.write(f'{self.tabs(9)}service {options["service-orig"]}\n') 
      else:
        f.write(f'{self.tabs(9)}service any;\n')
      self.static_to_interface(line)
      f.write(f'{self.tabs(9)}to-interface {self.static_to_interface(line)};\n')
    return 

if __name__ == '__main__':
  Convert = NatConversion()
  Convert.convert_all_nat()
