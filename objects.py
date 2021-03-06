# Takes ASA objects and coverts them into Palo Objects.  Eventually will create
# an excel showing mappings.

'''
Should create a function to pass to other modules that will pull required objects
for that specific module.  Ie nat.py/access_policy.py will also require ect..
'''

import re
from ciscoconfparse import CiscoConfParse

#FILENAME will be a argument passed from main.py once it is created.  FILENAME set statically for testing only.
#CONVERTED_FILENAME will likely follow suit but may default to a static path/string.
FILENAME = "./Configurations/ASA.txt"
CONVERTED_FILENAME = "./Configurations/Converted/convertedObjects.txt"

SEARCH_NETWORK_O = r'(object\s)(network\s)([A-Za-z-_\d.]*)'
SEARCH_NETWORK_G = r'(object-group\s)(network\s)([A-Za-z-_\d.]*)'
SEARCH_SERVICE_O = r'(object\s)(service\s)([A-Za-z-_\d.]*)'
SEARCH_SERVICE_G = r'(object-group\s)(service\s)([A-Za-z-_\d.]*)'

class Objects():
  def __init__(self, FILENAME, search_text):
    self.objects = self.find_objects(FILENAME, search_text)
    self.subnet_masks = {
      '255.255.255.255': '/32',
      '255.255.255.254': '/31',
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
      '255.254.0.0': '/15',
      '255.252.0.0': '/14',
      '255.248.0.0': '/13',
      '255.240.0.0': '/12',
      '255.224.0.0': '/11',
      '255.192.0.0': '/10',
      '255.128.0.0': '/9',
      '255.0.0.0': '/8',
      }
  
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
  
  def tabs(self, num_tabs):
    return '\t'*num_tabs

class Network(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_NETWORK_O)
    self.network_hosts = self.get_host_objs()
    self.network_subnets = self.get_subnet_objs()
    self.network_nat = self.get_nat_objs()
    self.network_fqdn = self.get_fqdn_objs()

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

  def create_address_header(self):
    with open(CONVERTED_FILENAME, 'w') as f:
      f.write(f'{self.tabs(5)}address {{\n')
      return

  def close_address_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}}}\n')

  def get_host_attr(self, host):
    attr = {}
    attr['obj_host_name'] = re.search(r'object\snetwork\s([\w\d\-._ ]*)', host[0]).group(1)
    attr['obj_host_addr'] = re.search(r'host\s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', ' '.join(host)).group(1)
    if(('description' in ' '.join(host)) and (re.search(r' description ([\S ]*)', ' '.join(host)) != None)):
      attr['obj_host_desc'] = re.search(r' description ([\S ]*)', ' '.join(host)).group(1)
    else:
      attr['obj_host_desc'] = False
    attr['ip_netmask'] = '/32'
    return attr

  def convert_host_objs(self):
    for host in self.network_hosts:
      attr = self.get_host_attr(host)
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}{attr.get("obj_host_name")} {{\n')
        f.write(f'{self.tabs(7)}ip-netmask {attr.get("obj_host_addr")}{attr.get("ip_netmask")};\n')
        if(attr.get("obj_host_desc")):
          f.write(f'{self.tabs(7)}description "{attr.get("obj_host_desc")}";\n')
        f.write(f'{self.tabs(6)}}}\n')
    for host in NetworkGroup().group_hosts:
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}H-{host} {{\n')
        f.write(f'{self.tabs(7)}ip-netmask {host}/32\n')
        f.write(f'{self.tabs(6)} }}\n')
    return
  
  def get_subnet_attr(self, net):
    attr = {}
    net_search = r'subnet (\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}) (\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})'
    net_cidr = self.subnet_masks[re.search(net_search, ' '.join(net)).group(2)]
    attr['obj_sub_name'] = 'N-' + re.search(net_search, ' '.join(net)).group(1) + '-' + net_cidr[1:]
    attr['obj_sub_addr'] = re.search(net_search, ' '.join(net)).group(1)
    attr['obj_sub_mask'] = re.search(net_search, ' '.join(net)).group(2)
    if(('description' in ' '.join(net)) and (re.search(r' description ([\S ]*)', ' '.join(net)) != None)):
      attr['obj_sub_desc'] = re.search(r' description ([\S ]*)', ' '.join(net)).group(1)
    else:
      attr['obj_host_desc'] = False
    attr['ip_netmask'] = net_cidr
    return attr

  def convert_subnet_objs(self):
    for net in self.network_subnets:
      attr = self.get_subnet_attr(net)
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}{attr["obj_sub_name"]} {{\n')
        f.write(f'{self.tabs(7)}ip-netmask {attr["obj_sub_addr"]}{attr["ip_netmask"]};\n')
        if(attr.get("obj_sub_desc")):
          f.write(f'{self.tabs(7)}description "{attr.get("obj_sub_desc")}";\n')
        f.write(f'{self.tabs(6)}}}\n')
    return

  def get_fqdn_attr(self, fqdn):
    attr = {}
    attr['obj_fqdn_name'] = re.search(r'object network (\S*)', ' '.join(fqdn)).group(1)
    attr['obj_fqdn_val'] = re.search(r'( fqdn (v4 |v5 )?)(\S*)', ' '.join(fqdn)).group(3)
    if(('description' in ' '.join(fqdn)) and (re.search(r' description ([\S ]*)', ' '.join(fqdn)) != None)):
      attr['obj_fqdn_desc'] = re.search(r' description ([\S ]*)', ' '.join(fqdn)).group(1)
    else:
      attr['obj_fqdn_desc'] = False
    return attr

  def convert_fqdn_objs(self):
    for fqdn in self.network_fqdn:
      attr = self.get_fqdn_attr(fqdn)
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}{attr["obj_fqdn_name"]} {{\n')
        f.write(f'{self.tabs(7)}fqdn {attr["obj_fqdn_val"]};\n')
        if(attr.get("obj_fqdn_desc")):
          f.write(f'{self.tabs(7)}description "{attr.get("obj_fqdn_desc")}";\n')
        f.write(f'{self.tabs(6)}}}\n')
    return


class NetworkGroup(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_NETWORK_G)
    self.network_groups = self.get_network_groups()
    self.group_hosts = self.get_group_hosts()

  def get_network_groups(self):
    filter = r'(object-group network )(\S*)'
    groups = self.filter_obj_types(filter)
    net_groups = []
    for group in groups:
      if('object-group network DM_INLINE_NETWORK' not in group[0]):
        net_groups.append(group)
    return net_groups

  def get_group_hosts(self):
    hosts = []
    for group in self.network_groups:
      for line in group:
        if(type(re.search(r'(network-object host )(\S*)', line)) != type(None)):
          hosts.append(re.search(r'(network-object host )(\S*)', line).group(2))
    return hosts

  def create_address_g_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}address-group {{\n')
      return

  def close_address_g_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}}}\n')

  def get_group_members(self, net_group):
    hosts = r'(network-object host )(\S*)'
    objs = r'(network-object object )(\S*)'
    subnets = r'(network-object )(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}) (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'
    group_obj = r'group-object ([\S ?]*)'
    members = []
    for line in net_group[1:]:
      if (type(re.search(hosts, line)) != type(None)):
        members.append('H-' + re.search(hosts, line).group(2))
      elif (type(re.search(objs, line)) != type(None)):
        members.append(re.search(objs, line).group(2))
      elif (type(re.search(group_obj, line)) != type(None)):
        members.append(re.search(group_obj, line).group(1))
      elif (type(re.search(subnets, line)) != type(None)):
        cidr = self.subnet_masks[re.search(subnets, line).group(3)]
        members.append('N-' + re.search(subnets, line).group(2)+'-'+cidr[1:])
      else:
        continue
    return members

  def convert_group_objs(self):
    self.create_address_g_header()
    for net_group in self.network_groups:
      with open(CONVERTED_FILENAME, 'a') as f:
        group_members = self.get_group_members(net_group)
        group_name = re.search(r'(object-group\snetwork\s)(\S*)', net_group[0]).group(2)
        f.write(f'{self.tabs(6)}{group_name} {{\n')
        f.write(f'{self.tabs(7)}static [ {" ".join(group_members)}];\n')
        f.write(f'{self.tabs(6)}}}\n')
    self.close_address_g_header()
    return


class Service(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_SERVICE_O)
    self.created_service_ranges = set()

  def convert_service_objs(self):
    self.create_header()
    self.append_defaults()
    for service in self.objects:
      service_attr = self.get_service_attributes(service)
      self.create_service(service_attr['name'])
      self.open_protocol()
      self.set_protocol_attr(service_attr)
      self.close_protocol()
      self.set_description(service_attr['description'])
      self.close_service()
    for group in ServiceGroupObjects.objects:
      for line in group:
        if ('tcp destination range' in line):
          self.create_tcp_range(line)
        elif('udp destination range' in line and type(re.search(r'destination\srange\s(\d*)\s(\d*)', line)) != type(None)):
          self.create_udp_range(line)
        elif ('tcp-udp destination range' in line):
          self.create_tcp_range(line)
          self.create_udp_range(line)
        else:
          continue
    self.close_header()

  def create_tcp_range(self, line):
    start_port = re.search(r'destination\srange\s(\d*)\s(\d*)', line).group(1)
    end_port =  re.search(r'destination\srange\s(\d*)\s(\d*)', line).group(2)
    port_range = f'tcp-range-{start_port}-{end_port}'
    if(port_range not in self.created_service_ranges):
      self.created_service_ranges.add(port_range)
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}{port_range} {{\n')
        f.write(f'{self.tabs(7)}protocol {{\n')
        f.write(f'{self.tabs(8)}tcp {{\n')
        f.write(f'{self.tabs(9)}port {start_port}-{end_port};\n')
      self.set_override()
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(8)}}}\n')
        f.write(f'{self.tabs(7)}}}\n')
        f.write(f'{self.tabs(6)}}}\n')
    else:
      return

  def create_udp_range(self, line):
    start_port = re.search(r'destination\srange\s(\d*)\s(\d*)', line).group(1)
    end_port =  re.search(r'destination\srange\s(\d*)\s(\d*)', line).group(2)
    port_range = f'udp-range-{start_port}-{end_port}'
    if(port_range not in self.created_service_ranges):
      self.created_service_ranges.add(port_range)
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(6)}{port_range} {{\n')
        f.write(f'{self.tabs(7)}protocol {{\n')
        f.write(f'{self.tabs(8)}tcp {{\n')
        f.write(f'{self.tabs(9)}port {start_port}-{end_port};\n')
      self.set_override()
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(8)}}}\n')
        f.write(f'{self.tabs(7)}}}\n')
        f.write(f'{self.tabs(6)}}}\n')
    else:
      return

  def get_service_attributes(self, service):
    service_attr = {}
    service_string = ' '.join(service)
    service_attr['name'] = re.search(r'object service (\S*)', service_string).group(1)
    service_attr['protocol'] = re.search(r'service\s(\S*)\s(source|destination)', service_string).group(1)
    if(type(re.search(r'destination\s(range\s)(\S*)\s(\S*)', service_string)) != type(None)):
      dst_start = re.search(r'destination\s(range\s)(\S*)\s(\S*)', service_string).group(2)
      dst_end = re.search(r'destination\s(range\s)(\S*)\s(\S*)', service_string).group(3)
      service_attr['destination'] = f'{dst_start}-{dst_end}'
    elif(type(re.search(r'destination\s(eq\s)(\S*)', service_string)) != type(None)):
      service_attr['destination'] = re.search(r'destination\s(eq\s)(\S*)', service_string).group(2)
    else:
      service_attr['destination'] = False
    if(type(re.search(r'source\s(range\s)(\S*)\s(\S*)', service_string)) != type(None)):
      source_start = re.search(r'source\s(range\s)(\S*)\s(\S*)', service_string).group(2)
      source_end = re.search(r'source\s(range\s)(\S*)\s(\S*)', service_string).group(3)
      service_attr['source'] = f'{source_start}-{source_end}'
    elif(type(re.search(r'source\s(eq\s)(\S*)', service_string)) != type(None)):
      service_attr['source'] = re.search(r'source\s(eq\s)(\S*)', service_string).group(2)
    else:
      service_attr['source'] = False
    if(type(re.search(r'\sdescription\s(.*)', service_string)) != type(None)):
      service_attr['description'] = re.search(r'\sdescription\s(.*)', service_string).group(1)
    else:
      service_attr['description'] = False
    return service_attr

  def set_protocol_attr(self, attr):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(8)}{attr["protocol"]} {{\n')
      if(attr["destination"]):
        f.write(f'{self.tabs(9)}port {attr["destination"]};\n')
      if(attr["source"]):
        f.write(f'{self.tabs(9)}source-port {attr["source"]};\n')
    self.set_override()
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(8)}}}\n')

  def set_description(self, description):
    if(description):
      with open(CONVERTED_FILENAME, 'a') as f:
        f.write(f'{self.tabs(7)}description "{description}";\n')
    return

  def append_defaults(self, default_file='./Defaults/service_obj.txt'):
    '''
    Appends service-object defaults (ie www https)to account for those objects referenced in ASA 
    that aren't explicitly called out in the configuration.
    '''
    try:
      with open(CONVERTED_FILENAME, 'a') as f:
        with open(default_file, 'r') as def_f:
          for line in def_f:
            f.write(line)
      return
    except:
      print('./Defaults/service_obj.txt not found.')
      return
  
  def set_override(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(9)}override {{\n')
      f.write(f'{self.tabs(10)}no;\n')
      f.write(f'{self.tabs(9)}}}\n')

  def open_protocol(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(7)}protocol {{\n')
    
  def close_protocol(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(7)}}}\n')

  def create_service(self, name):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}{name} {{\n')
  
  def close_service(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}}}\n')

  def create_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}service {{\n')
  
  def close_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}}}\n')

class ServiceGroup(Objects):
  def __init__(self):
    super().__init__(FILENAME=FILENAME, search_text=SEARCH_SERVICE_G)

  def convert_service_groups(self):
    self.create_header()
    for group in self.objects:
      if("DM_INLINE" not in ' '.join(group)):
        group_attr = self.get_group_attr(group)
        self.open_group_name(group_attr['name'])
        self.add_members(group)
        self.close_group_name()
    self.close_header()

  def get_group_attr(self, group):
    g_string = ' '.join(group)
    attr = {}
    attr['name'] = re.search(r'object-group service (\S*)', g_string).group(1)
    attr['description'] = self.get_description(group)
    return attr

  def get_description(self, group):
    description = ''
    for line in group:
      if('description' in line):
        description = re.search(r'\sdescription\s([\S ]*)',line).group(1)
        return description
    return False

  def add_members(self, group):
    members = self.get_members(group)
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(7)}members {members}\n')

  def get_members(self, group):
    members = []
    for member in group:
      if('service-object' in member):
        if(self.get_service_object(member) != ''):
          members.append(self.get_service_object(member))
      # if('protocol-object' in member):
      #   #members.append(member)
      # if('port-object' in member):
      #   #members.append(member)
      # if('group-object' in member):
      #   #members.append(member)
    print(members)
    return f"[ {' '.join(members)}];"

  def get_service_object(self, member):
    if('tcp ' in member):
      return self.tcp_service_obj(member)
    elif(' udp' in member):
      return self.udp_service_obj(member)
    elif('tcp-udp' in member):
      return self.tcp_udp_service_obj(member)
    elif('service-object object ' in member):
      return re.search(r'service-object object\s([\dA-Za-z\-_]*)', member).group(1)
    #ICMP
    elif(type(re.search(r'(service-object\s)(icmp)\s?(\S*)?', member)) != type(None)):
      return 'ICMP-obj'
    #UNMATCHED SERVICE OBJECTS--NEEDS HANDLED
    else:
      return 'SERV_obj'

  def tcp_service_obj(self, member):
    if(type(re.search(r'service-object tcp\sdestination\seq\s(\d{1,5})', member)) != type(None)):
      tcp_port = re.search(r'service-object tcp\sdestination\seq\s(\d{1,5})', member).group(1)
      return f'tcp-{tcp_port}'
    if(type(re.search(r'tcp destination\seq\s(\S*)', member)) != type(None)):
      if('sip' in member):
        return 'sip_tcp'
      elif('domain' in member):
        return 'domain_tcp'
      elif('www' in member):
        return 'www_tcp'
      else:
        tcp_port = (re.search(r'tcp destination\seq\s(\S*)', member).group(1))
        return tcp_port
    if(type(re.search(r'tcp\sdestination\srange\s(\d*)\s(\d*)', member)) != type(None)):
      tcp_start = re.search(r'tcp\sdestination\srange\s(\d*)\s(\d*)', member).group(1)
      tcp_end = re.search(r'tcp\sdestination\srange\s(\d*)\s(\d*)', member).group(2)
      tcp_range = f'{tcp_start}-{tcp_end}'
      return f'tcp-range-{tcp_range}'

  def udp_service_obj(self, member):
    if(type(re.search(r'udp\sdestination\seq\s(\d{1,5})', member)) != type(None)):
      udp_port = (re.search(r'udp\sdestination\seq\s(\d{1,5})', member).group(1))
      return f'udp-{udp_port}'
    elif(type(re.search(r'service-object object (\S*)', member)) != type(None)):
      udp_port = re.search(r'service-object object (\S*)', member).group(1)
      return udp_port
    else:
      return ''

  def tcp_udp_service_obj(self, member):
    if('destination range' in member):
      tcp_udp_start = re.search(r'destination\srange\s(\d*)\s(\d*)', member).group(1)
      tcp_udp_end = re.search(r'destination\srange\s(\d*)\s(\d*)', member).group(2)
      return f'tcp-range-{tcp_udp_start}-{tcp_udp_end} udp-range-{tcp_udp_start}-{tcp_udp_end}'
    else:
      return ''

  def open_group_name(self, name):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}{name} {{\n')

  def close_group_name(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(6)}}}\n')

  def create_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}service-group {{\n')

  def close_header(self):
    with open(CONVERTED_FILENAME, 'a') as f:
      f.write(f'{self.tabs(5)}}}\n')




if __name__ == '__main__':
  #Create Configuration Objects as Python Objects
  NetworkObjects = Network()
  NetworkGroupObjects = NetworkGroup()
  ServiceObjects = Service()
  ServiceGroupObjects = ServiceGroup()

  #Run Object Conversion Functions
  NetworkObjects.create_address_header()
  NetworkObjects.convert_host_objs()
  NetworkObjects.convert_subnet_objs()
  NetworkObjects.convert_fqdn_objs()
  NetworkObjects.close_address_header()
  NetworkGroupObjects.convert_group_objs()
  ServiceObjects.convert_service_objs()
  #testing ------BELOW---------
  ServiceGroupObjects.convert_service_groups()