from ciscoconfparse import CiscoConfParse
import re

#temporarily set filename and search strings
#will be moved to main.py later. filename and converted filename will be passed as arguments
#pulled using file-explorer from the mainapp.;

filename = "./Configurations/ASA.txt"
converted_filename = "./Configurations/Converted/convertedInterface.txt"
regex = r'(interface )([G,T,F][a-zA-Z]+)(\s?\d[/]\d\d?[/]?\d?\d?)'
subnet_masks = {
  '255.255.255.255': '/32',
  '255.255.255.252': '/30',
  '255.255.255.248': '/29',
  '255.255.255.240': '/28',
  '255.255.255.224': '/27',
  '255.255.255.192': '/26',
  '255.255.255.128': '/25',
  '255.255.255.0': '/24',
  '255.255.254.0': '/23',
  '255.255.252.0': '/22',
  '255.255.248.0': '/21',
  '255.255.240.0': '/20',
  '255.255.224.0': '/19',
  '255.255.192.0': '/18',
  '255.255.128.0': '/17',
  '255.255.0.0': '/16',
}


#find all interfaces
def find_interfaces (file=filename, text=regex):
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


#find Domain-name.  Function will be moved out of interfaces.py
#once main.py is built.
def find_domain(file, text):
  '''
  Returns the domain name from the ASA config
  Takes an ASA config and Search string.
  '''
  parse = CiscoConfParse(file)
  domain = parse.find_objects(text)[0]
  return domain.replace('domain-name ', '')
domain_name = (find_domain (filename, 'domain-name'))

#filter out the shutdown interfaces
def filter_shutdown(interface_list):
  online_interfaces = []
  for interface_obj in interface_list:
    if not " shutdown" in interface_obj:
      online_interfaces.append(interface_obj)
  return online_interfaces

#Create the parent Palo container for interfaces    
def palo_device_parent(filename=converted_filename, domain_name=domain_name):
  f = open(filename, 'w')
  f.write('config {\n')
  f.write('\tdevices {\n')
  if domain_name:
    f.write(f'\t\t{domain_name} {{\n')
  else:
    f.write(f'\t\tlocalhost.localdomain {{\n')
  f.write('\t\t\tinterface {\n')
  f.write('\t\t\t\tethernet {')
  f.close()

def palo_device_parent_close(filename=converted_filename):
  f = open(filename, 'a')
  f.write('\n\t\t\t\t}')
  f.write('\n\t\t\t}')
  f.write('\n\t\t}')
  f.write('\n\t}')
  f.write('\n}')
  f.close()

def palo_ipv6(interface, filename=converted_filename):
  '''
  Needs functionality added
  '''
  f = open(f'./Configurations/Converted/convertedInterface.txt', 'a')
  f.write(f'\n\t\t\t\t\t\tlayer3 {{')
  f.write(f'\n\t\t\t\t\t\t\tipv6 {{')
  f.write(f'\n\t\t\t\t\t\t\t\tneighbor-discovery {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\trouter-advertisement {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\tenable no;')
  f.write(f'\n\t\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t}}')
  f.close()

def palo_units_ipv6(interface, filename=converted_filename):
  '''
  Needs functionality added
  '''
  f = open(f'./Configurations/Converted/convertedInterface.txt', 'a')
  f.write(f'\n\t\t\t\t\t\t\t\t\tipv6 {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\tneighbor-discovery {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\t\trouter-advertisement {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\t\t\tenable no;')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t\t\t}}')
  f.close()

def palo_ndp_proxy(interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  f.write(f'\n\t\t\t\t\t\t\tndp-proxy {{\n')
  f.write(f'\t\t\t\t\t\t\t\tenabled no;\n')
  f.write(f'\t\t\t\t\t\t\t}}')
  f.close()

def palo_units_ndp_proxy(interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  f.write(f'\n\t\t\t\t\t\t\t\t\tndp-proxy {{\n')
  f.write(f'\t\t\t\t\t\t\t\t\t\tenabled no;\n')
  f.write(f'\t\t\t\t\t\t\t\t\t}}')
  f.close()

def palo_ipv4(interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  has_address = False
  #check for addresses
  for line in interface:
    if 'address' in line:
      has_address = True
      f.write(f'\n\t\t\t\t\t\t\tip {{\n')
      break
  #open the interface config parent and configure address
  if has_address:
    addr_search = re.compile(r'(\d+[.]\d+[.]\d+[.]\d+)\s(\d+[.]\d+[.]\d+[.]\d+)')
    for line in interface:
      if 'address' in line:
        ip_addr = re.search(addr_search, line).group(1)
        mask = re.search(addr_search, line).group(2)
        f.write(f'\t\t\t\t\t\t\t\t{ip_addr}{subnet_masks[mask]}\n')
      else:
        continue
    f.write(f'\t\t\t\t\t\t\t}}\n')
    f.close()
    return
  else:
    f.close()
    return

def palo_units_ipv4(interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  has_address = False
  #check for addresses
  for line in interface:
    if 'address' in line:
      has_address = True
      f.write(f'\n\t\t\t\t\t\t\t\t\tip {{\n')
      break
  #open the interface config parent and configure address
  if has_address:
    addr_search = re.compile(r'(\d+[.]\d+[.]\d+[.]\d+)\s(\d+[.]\d+[.]\d+[.]\d+)')
    for line in interface:
      if 'address' in line:
        ip_addr = re.search(addr_search, line).group(1)
        mask = re.search(addr_search, line).group(2)
        f.write(f'\t\t\t\t\t\t\t\t\t\t{ip_addr}{subnet_masks[mask]}\n')
      else:
        continue
    f.write(f'\t\t\t\t\t\t\t\t\t}}')
    f.close()
    return
  else:
    f.close()
    return

def palo_lldp(filename=converted_filename):
  #asa will never have lldp or cdp enabled.
  #configuring lldp to off on palo. may opt for user
  #configurable option later.
  f = open(converted_filename, 'a')
  f.write('\t\t\t\t\t\t\tlldp {\n')
  f.write('\t\t\t\t\t\t\t\tenable no;\n')
  f.write('\t\t\t\t\t\t\t}\n')
  f.close()

def palo_units_lldp(filename=converted_filename):
  '''
  asa will never have lldp or cdp enabled.
  configuring lldp to off on palo. may opt for user
  configurable option from main.py later.
  '''
  f = open(converted_filename, 'a')
  f.write('\n\t\t\t\t\t\t\t\t\tlldp {\n')
  f.write('\t\t\t\t\t\t\t\t\t\tenable no;\n')
  f.write('\t\t\t\t\t\t\t\t\t}')
  f.close()

#needs Cisco function check functionality added
def palo_adjust_tcp(filename=converted_filename):
  #asa will never have lldp or cdp enabled.
  #configuring lldp to off on palo. may opt for user
  #configurable option later.
  f = open(converted_filename, 'a')
  f.write('\t\t\t\t\t\t\tadjust-tcp-mss {\n')
  f.write('\t\t\t\t\t\t\t\tenable no;\n')
  f.write('\t\t\t\t\t\t\t}\n')
  f.close()

def palo_units_adjust_tcp(filename=converted_filename):
  #asa will never have lldp or cdp enabled.
  #configuring lldp to off on palo. may opt for user
  #configurable option later.
  f = open(converted_filename, 'a')
  f.write('\n\t\t\t\t\t\t\t\t\tadjust-tcp-mss {\n')
  f.write('\t\t\t\t\t\t\t\t\t\tenable no;\n')
  f.write('\t\t\t\t\t\t\t\t\t}')
  f.close()

def is_subInterface(interface, filename=converted_filename):
  f = open(filename, 'r')
  contents = f.read()
  f.close()
  if ('.' in interface[0]):
    old_content = contents.split("\n")
    new_content = "\n".join(old_content[:-2])
    f = open(filename, 'w+')
    for i in range(len(new_content)):
      f.write(new_content[i])
    f.close()
    return True
  else:
    f.close()
    return False

def palo_units_tag(interface, filename=converted_filename):
  #check for vlan tag.  add vlan tag to units>interface if found
  for config_item in interface:
    if ('vlan' in config_item):
      tag_search = r'([v][l][a][n]\s)(\d+)'
      tag_number = re.search(tag_search, config_item)
      f = open(converted_filename, 'a')
      f.write(f'\n\t\t\t\t\t\t\t\t\ttag {tag_number.group(2)};')
      f.close()

def palo_header(interface, filename=converted_filename):
  head_int_search = r'(interface )([a-zA-z]+)(\d\d?)([\/]\d\d?[\/]?\d?\d?)'
  header = re.search(head_int_search, interface)
  f = open(converted_filename, 'a')
  f.write(f'\n\t\t\t\t\tethernet1{header.group(4)}')
  f.close()
  return

def palo_units_header(interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  head_int_search = r'(\d\d?[.]\d\d?\d?)'
  header = re.search(head_int_search, interface[0])
  f.write('\n\t\t\t\t\t\t\tunits {')
  f.write(f'\n\t\t\t\t\t\t\t\tethernet{header.group(0)}  {{')
  f.close()
  return

def palo_int_footer(filename=converted_filename):
  f = open(filename, 'a')
  f.write('\t\t\t\t\t\t}')
  f.write('\n\t\t\t\t\t}')
  f.close()

def palo_units_footer(filename=converted_filename):
  f = open(converted_filename, 'a')
  f.write('\n\t\t\t\t\t\t\t\t}')#headerclose
  f.write('\n\t\t\t\t\t\t\t}')#unitclose
  f.close()
  return

def palo_units(interface):
  palo_units_header(interface)
  palo_units_ipv6(interface)
  palo_units_ndp_proxy(interface)
  palo_units_adjust_tcp(interface)
  palo_units_ipv4(interface)
  palo_units_tag(interface)
  palo_units_footer()

#Main Conversion Function -- Converts ASA interface config to Palo Interface Config.
def palo_convert_interfaces(interfaces, filename=filename):
  for interface in interfaces:
    if (is_subInterface(interface)):
      palo_units(interface)
      continue
    else:
      palo_header(interface[0])
      palo_ipv6(interface)
      palo_ndp_proxy(interface)
      palo_ipv4(interface)
      palo_lldp()
      palo_int_footer()


#Main build loop.
if __name__ == '__main__':
  interface_list = (find_interfaces (filename, regex))
  filtered_interfaces = filter_shutdown(interface_list)
  def convert_interfaces(filename, regex):
    palo_device_parent()
    palo_convert_interfaces(filtered_interfaces)
    palo_device_parent_close()
    return

  convert_interfaces(filename, regex)

# for interface_obj in online_interfaces:
#   print('\n')
#   for config in interface_obj:
#     print(config)