# Takes ASA objects and coverts them into Palo Objects.  Eventually will create
# an excel showing mappings.

import re
from ciscoconfparse import CiscoConfParse

ASA_Config = open("./Configurations/ASA.txt", 'r')
ASA_Pattern = r'(interface )([G,T,F][a-zA-Z]+)(\s?\d[/]\d\d?[/]?\d?\d?)'
test = 'testing interface GigabitEthernet0/0/0 string'


for i, line in enumerate(ASA_Config):
  for match in re.finditer(ASA_Pattern, line):
    interface_obj = {
    "asa_if": match.group(2)+match.group(3),
    }

    print(interface_obj)



interface_re =  re.search(ASA_Pattern, test)
ASA_Config.close()

