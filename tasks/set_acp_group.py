import re

# //FILES.  CURRENTLY YOU NEED TO WORK WITH JUST THE GROUP PORTION OF THE CONFIGURATION.  I WANT TO AUTOMATE THIS IN THE FUTURE.
FILENAME = "C:/Users/zacha/Desktop/PYTHON/NETWORKING/PALO-CONVERTER/Configurations/Group_Profile/cut_groups.xml"
OUTPUT_FILE = "./tasks/set_commands.txt"

# //PROFILE NAME YOU WANT TO APPLY TO EACH ACCESS-POLICY
PROFILE_NAME = "MY_PROFILE"

# //PLACEHOLDER REG TO AUTOMATE SELECTING THE RULES FROM ENTIRE CONFIG. 
SEC_RULE_START_REG = r'placeholder'
SEC_RULE_END_REG = r'placeholder'

# //FINDS XML HEADERS.  NAME VALUES ARE GROUP1
SEC_RULE_REG = r'<entry\sname=\"([\w\s\-\_\*\!\#\%\^\&\@\(\)\=\+\,\.\/\;\:\']*)'


# //READ IN THE FILE AS A STRING
with open(FILENAME, 'r') as file:
    contents = file.read()

# //FIND UNIQUE ACCESS-POLICY NAMES
matches = re.findall(SEC_RULE_REG, contents)

# //CREATE SET OUTPUT FOR EACH MATCH
set_output = []
for match in matches:
    set_output.append(f'set rulebase security rules "{match}" profile-setting group {PROFILE_NAME}\n')

with open(OUTPUT_FILE, 'w') as f:
    for command in set_output:
        f.write(command)