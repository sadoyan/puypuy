from configparser import ConfigParser
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

print(bcolors.OKGREEN + "Please give me some information to configure OddEye agent" + bcolors.OKGREEN)
print(bcolors.ENDC + " " + bcolors.ENDC)

url = 'https://api.oddeye.co/oddeye-barlus/put/tsdb'
sandbox = 'False'
err_handler = 2
tsdtype = 'OddEye'
check_period = 10
debug_log = 'False'
max_cache = 50000


uuid = input("Please enter your UID: ")
run_user = input("unprivileged system account for Agent: ")
log_file = input("Full path for log file (Should be writable for Agent's system user): ")
pid_file = input("Full path for pid file(Should be writable for Agent's system user): ")
tmpdir = input("Full path for temp files(Should be writable for Agent's system user): ")
location = input("Your servers location(Aka : us-east-1): ")
cluster_name = input("Friendly name of your cluster: ")
host_group = input("Grouping TAG of hosts: ")


conf_system_checks = input("Do you want me to enable basic system checks (yes/no): ")
while conf_system_checks not in ['yes', 'no']:
    print(bcolors.FAIL + 'Please write yes or no ' + bcolors.FAIL)
    conf_system_checks = input("Do you want me to enable basic system checks (yes/no): ")

parser = ConfigParser()
config_file = 'conf/config.ini'

parser.read(config_file)

parser['TSDB'] = {'url': url, 'uuid': uuid, 'sandbox': 'False', 'err_handler': '2', 'tsdtype': 'OddEye'}
parser['SelfConfig'] = {'check_period_seconds': check_period, 'log_file': log_file, 'pid_file': pid_file,
                          'cluster_name': cluster_name, 'host_group': host_group, 'tmpdir': tmpdir,
                          'debug_log': 'False', 'run_user': run_user, 'max_cache': '50000', 'location': location}

with open(config_file, 'w') as configfile:
 parser.write(configfile)

src = (os.path.dirname(os.path.realpath("__file__"))+'/checks_available')
dst = (os.path.dirname(os.path.realpath("__file__"))+'/checks_enabled')
os.chdir(dst)

syschecks = ('check_cpustats.py', 'check_disks.py', 'check_load_average.py', 'check_memory.py', 'check_network_bytes.py', 'check_oddeye.py')

if conf_system_checks == 'yes':
    for syscheck in syschecks:
        os.symlink('../checks_available/' + syscheck, './' + syscheck)
    print(bcolors.OKGREEN + 'System checks are configured, please restart agent to enable' + bcolors.OKGREEN)
elif conf_system_checks == 'no':
    print(bcolors.OKGREEN + ' ' + bcolors.OKGREEN)
    print(bcolors.OKGREEN + 'Done, please do not forget to configure and enable checks suitable for you system' + bcolors.OKGREEN)
else:
    print(bcolors.FAIL + ' ' + bcolors.FAIL)
    print(bcolors.FAIL + 'Failed to enable systems checks, please enable it manually' + bcolors.FAIL)