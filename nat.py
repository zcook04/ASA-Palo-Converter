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

#FILENAME will be a argument passed from main.py once it is created.  FILENAME set statically for testing only.
#CONVERTED_FILENAME will likely follow suit but may default to a static path/string.
FILENAME = "./Configurations/ASA.txt"
CONVERTED_FILENAME = "./Configurations/Converted/convertedNat.txt"

STATIC_NAT_REGEX = r'(nat\s\()(\w*)([,])(\w*)(\)\s\w*\s)(static\s)'
STATIC_AFTER_AUTO = r'(nat\s\()(\w*)([,])(\w*)\)\s(after-auto)'

class NatConversion():
  def __init__(self, FILENAME=FILENAME, CONVERTED_FILENAME=CONVERTED_FILENAME):
    self.nat_index = 1
    self.FILENAME = FILENAME
    self.CONVERTED_FILENAME = CONVERTED_FILENAME
    self.static_nats = self.get_nat(FILENAME, STATIC_NAT_REGEX)
    self.auto_source_nats = self.get_nat(FILENAME, STATIC_AFTER_AUTO)

  def palo_static_nat(self):
    if (self.static_nats):
      for s_nat in self.static_nats:
        for line in s_nat:
          self.create_nat_rule_header()
          self.create_nat_source_translation()
          self.create_static_ip(line)
          self.close_static_ip()
          self.close_nat_source_translation()
          self.set_nat_rule_attributes(line)
          self.create_nat_rule_footer()
          self.increment_index()
      return
    else:
      return

  def palo_obj_nat(self):
    for o_nat in Network().get_nat_objs():
      attr = self.get_obj_attributes(o_nat)
      self.create_nat_rule_header()
      self.create_nat_source_translation()
      self.create_source_param(attr)
      self.close_source_param()
      self.close_nat_source_translation()
      self.set_obj_attributes(attr)
      self.create_nat_rule_footer()
      self.increment_index()

  def palo_after_auto_nat(self):
    if (self.static_nats):
      for s_nat in self.auto_source_nats:
        for line in s_nat:
          self.create_nat_rule_header()
          self.create_nat_source_translation()
          self.create_static_ip(line)
          self.close_static_ip()
          self.close_nat_source_translation()
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
    self.palo_obj_nat()
    self.palo_after_auto_nat()
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

  def create_nat_source_translation(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}source-translation {{\n')
    return

  def close_nat_source_translation(self):
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
      if ('after-auto' in line_array):
        f.write(f'{self.tabs(9)}source {line_array[6]};\n')
      else:
        f.write(f'{self.tabs(9)}source {line_array[4]};\n')
    return

  def static_to_interface(self, line):
    search_int_name = r'(nameif\s)(\w*)'
    search_line_name = r'(nat\s)(\(\w*[,])(\w*)'
    for intf in filtered_interfaces:
      s_intf = ' '.join(intf)
      int_name = re.search(search_int_name, s_intf)
      line_name = re.search(search_line_name, line)
      int_num = self.get_int_num(intf)
      if(int_name.group(2) == line_name.group(3)):
        return f'interface1/{int_num}'
      

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

  def create_source_param(self, attr):
    ip_type, translated, bi_directional = attr['ip_type'], attr['translated'], attr['bi_directional']
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(10)}{ip_type} {{\n')
      f.write(f'{self.tabs(11)}translated-address {translated}\n')
      if (bi_directional):
        f.write(f'{self.tabs(11)}bi-directional yes;')

  def close_source_param(self):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(10)}}}\n')
    return

  def get_obj_attributes(self, obj_nat):
    obj_nat_attr = {}
    obj_nat_attr['source'] = re.search(r'(object\s)(network)([\s])(.*)', obj_nat[0]).group(4)
    obj_nat_attr['szone'] = re.search(r'(nat \()([\w\-_\d]*)[,]([a-zA-Z\d_\-]*)\)\s([a-zA-Z\d_\-]*)\s([a-zA-Z\d_\-]*)', obj_nat[1]).group(2)
    obj_nat_attr['dzone'] = re.search(r'(nat \()([\w\-_\d]*)[,]([a-zA-Z\d_\-]*)\)\s([a-zA-Z\d_\-]*)\s([a-zA-Z\d_\-]*)', obj_nat[1]).group(3)
    if (re.search(r'(nat \()([\w\-_\d]*)[,]([a-zA-Z\d_\-]*)\)\s([a-zA-Z\d_\-]*)\s([a-zA-Z\d_\-]*)', obj_nat[1]).group(4) == 'dynamic'):
      obj_nat_attr['ip_type'] = 'dynamic-ip-and-port'
    else:
      obj_nat_attr['ip_type'] = 'static'
    obj_nat_attr['translated'] = re.search(r'(nat \()([\w\-_\d]*)[,]([a-zA-Z\d_\-]*)\)\s([a-zA-Z\d_\-]*)\s([a-zA-Z\d_\-.]*)', obj_nat[1]).group(5)
    obj_nat_attr['bi_directional'] = False #Logic function needed
    if (type((re.search(r'(pat-pool\s)([a-zA-Z\-_.\d]*)', obj_nat[1]))) is not type(None)):
      obj_nat_attr['pat-pool'] = re.search(r'(pat-pool\s)([a-zA-Z\-_.\d]*)', obj_nat[1]).group(2)
    return obj_nat_attr

  def set_obj_attributes(self, attr):
    with open(self.CONVERTED_FILENAME, 'a') as f:
      dzone, szone, source = attr['dzone'], attr['szone'], attr['source']
      f.write(f'{self.tabs(9)}to {dzone};\n')
      f.write(f'{self.tabs(9)}from {szone};\n')
      f.write(f'{self.tabs(9)}source {source};\n')
      f.write(f'{self.tabs(9)}destination any;\n')
      f.write(f'{self.tabs(9)}service any;\n') #needs logic function
      f.write(f'{self.tabs(9)}to-interface {self.obj_to_interface(dzone)};\n')
    return

  def obj_to_interface(self, dzone):
    search_int_name = r'(nameif\s)(\w*)'
    for intf in filtered_interfaces:
      s_intf = ' '.join(intf)
      int_name = re.search(search_int_name, s_intf)
      int_num = self.get_int_num(intf)
      if(int_name.group(2) == dzone):
        return f'ethernet1/{int_num}'

  def get_int_num(self, intf):
    search_int_num = r'(interface\s)([\w\d]*[\/])([\d.]*)(\/)?([\d.]*)?'
    int_number = re.search(search_int_num, intf[0])
    if (int_number.group(5) != ''):
      return int_number.group(5)
    else:
      return int_number.group(3)
      


if __name__ == '__main__':
  Convert = NatConversion()
  Convert.convert_all_nat()
