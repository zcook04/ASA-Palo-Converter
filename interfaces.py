from ciscoconfparse import CiscoConfParse
import re

#set filename and search strings
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
def find_interfaces (file, text):
	parent= [] #container to hold parent values
	parse = CiscoConfParse(file) #Parse config file
  #Filtering our parse for parents containing 'text'
	for obj in parse.find_objects(text):
		each_obj = []
		each_obj.append(obj.text)
		for each in obj.all_children:
			each_obj.append(each.text)
		parent.append(each_obj)
	return parent

#filter out the shutdown interfaces
def filter_shutdown(interface_list):
  online_interfaces = []
  for interface_obj in interface_list:
    if not " shutdown" in interface_obj:
      online_interfaces.append(interface_obj)
  return online_interfaces

#Create the parent Palo container for interfaces    
def palo_device_parent(filename=converted_filename, hostname='localhost.localdomain'):
  f = open(filename, 'w')
  f.write('config {\n')
  f.write('\tdevices {\n')
  f.write(f'\t\t{hostname} {{\n')
  f.write('\t\t\tinterface {\n')
  f.write('\t\t\t\tethernet {')
  f.close()

def palo_ipv6_int(index, interface, filename=converted_filename):
  f = open(f'./Configurations/Converted/convertedInterface.txt', 'a')
  f.write(f'\n\t\t\t\t\tethernet1/{index+1} {{')
  f.write(f'\n\t\t\t\t\t\tlayer3 {{')
  f.write(f'\n\t\t\t\t\t\t\tipv6 {{')
  f.write(f'\n\t\t\t\t\t\t\t\tneighbor-discovery {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\trouter-advertisement {{')
  f.write(f'\n\t\t\t\t\t\t\t\t\t\tenable no;')
  f.write(f'\n\t\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t\t}}')
  f.write(f'\n\t\t\t\t\t\t\t}}')
  f.close()

def palo_ndp_proxy(index, interface, filename=converted_filename):
  f = open(f'./Configurations/Converted/convertedInterface.txt', 'a')
  f.write(f'\n\t\t\t\t\t\t\tndp-proxy {{\n')
  f.write(f'\t\t\t\t\t\t\t\tenabled no;\n')
  f.write(f'\t\t\t\t\t\t\t}}')
  f.close()

def palo_ipv4(index, interface, filename=converted_filename):
  f = open(converted_filename, 'a')
  #check for addresses
  for line in interface:
    has_address = False
    if 'address' in line:
      has_address = True
      f.write(f'\n\t\t\t\t\t\t\tip {{\n')
      break
  #open the interface config parent
  if has_address:
    addr_reg = re.compile(r'(\d+[.]\d+[.]\d+[.]\d+)\s(\d+[.]\d+[.]\d+[.]\d+)')
    for line in interface:
      if 'address' in line:
        ip_addr = re.search(addr_reg, line).group(1)
        mask = re.search(addr_reg, line).group(2)
        f.write(f'\t\t\t\t\t\t\t\t{ip_addr}{subnet_masks[mask]}\n')
      else:
        continue

  f.write(f'\t\t\t\t\t\t\t}}\n')
  f.close()
  return


#Main Conversion Function -- Converts ASA interface config to Palo Interface Config.
def palo_convert_interfaces(interfaces, filename=filename):
  for index, interface in enumerate(interfaces):
    palo_ipv6_int(index, interface)
    palo_ndp_proxy(index, interface)
    palo_ipv4(index, interface)


#Main build loop. Interfaces to Palo Config
if __name__ == '__main__':
  def convert_interfaces(filename, regex):
    interface_list = (find_interfaces (filename, regex))
    filtered_interfaces = filter_shutdown(interface_list)
    palo_device_parent()
    palo_convert_interfaces(filtered_interfaces)
    return

  convert_interfaces(filename, regex)

# for interface_obj in online_interfaces:
#   print('\n')
#   for config in interface_obj:
#     print(config)