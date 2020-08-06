# Takes ASA objects and coverts them into Palo Objects.  Eventually will create
# an excel showing mappings.

import re 
ASA_Config = open("./Configurations/ASA.txt", 'r')
ASA_Pattern = r'(interface )([G,T,F][a-zA-Z]+)(\s?\d[/]\d\d?[/]?\d?\d?)'
test = 'testing interface GigabitEthernet0/0/0 string'
interface_re =  re.search(ASA_Pattern, test)
ASA_Config.close()

print(interface_re.group(0))
