#!/usr/bin/env python3

from configparser import ConfigParser
import os
import pwd
import getpass
import grp
import sys
import subprocess

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

sandbox = 'False'
error_handler = 2
tsdtype = 'OddEye'
check_period = 10
debug_log = 'False'
max_cache = 50000


run_user = input("unprivileged system account for Agent (defaults to current running user): ")
input_base_dir = input("Please input directory name for storing runtime files (defaults to current working directory):")
shorthosts = input('Shall I use short hostname of this machine instead of FQDN ?: (yes/no): ')
if shorthosts.lower() != 'yes' and shorthosts.lower() != 'no':
    print('Wrong input, defaulting to yes')
    shorthosts = 'yes'

if input_base_dir == '':
    input_base_dir = os.getcwd()

base_dir = input_base_dir.rstrip('/')
log_file = base_dir + '/var/puypuy.log'
pid_file = base_dir + '/var/puypuy.pid'
tmpdir = base_dir + '/var/puypuy_tmp'
location = input("Your servers location (Aka : us-east-1): ")
cluster_name = input("Friendly name of your cluster: ")
host_group = input("Grouping TAG of hosts: ")

if not os.path.exists(base_dir + '/var'):
    os.mkdir(base_dir + '/var')
if not os.path.exists(tmpdir):
    os.mkdir(tmpdir)

if run_user == '':
    uid = os.getuid()
    gid = os.getgid()
    run_user = getpass.getuser()
else:
    uid = pwd.getpwnam(run_user).pw_uid
    gid = pwd.getpwnam(run_user).pw_gid

for root, dirs, files in os.walk(base_dir, topdown=False):
    for name in files:
        os.chown((os.path.join(root, name)), uid, gid)
    for name in dirs:
        os.chown((os.path.join(root, name)), uid, gid)

conf_system_checks = input("Do you want me to enable basic system checks (yes/no): ")
systemd_service = input("Do you want to run PuyPuy at system boot (yes/no): ")

conf_tsdb_type = input("Please select DB server (InfluxDB / InfluxDB2 / OpenTSDB / KairosDB / Carbon): ")


while conf_system_checks not in ['yes', 'no']:
    print(bcolors.FAIL + 'Please write yes or no ' + bcolors.FAIL)
    conf_system_checks = input("Do you want me to enable basic system checks (yes/no): ")

parser = ConfigParser()
config_file = 'conf/config.ini'
parser.read(config_file)
service_file = '/lib/systemd/system/oe-agent.service'
sparser = ConfigParser()
sparser.optionxform = str

if conf_tsdb_type == 'InfluxDB':
    address = input('Please enter InfluxDB address, defaults to http://127.0.0.1:8086: ')
    if address == '':
        address = 'http://127.0.0.1:8086'
    idb = input('What is your InfluxDB database: ')
    auth = input('Have you enabled authentication in InfluxDB ? (yes/no): ')
    if auth.lower() == 'yes':
        ia = 'True'
        iu = input('Username for InfluxDB: ')
        ip = input('Password for InfluxDB: ')
    elif auth.lower() == 'False':
        ia = 'False'
        iu = 'placeholder'
        ip = 'placeholder'
    else:
        print('Your input was wrong, will disable InfluxDB authentication in config: ')
        ia = 'False'
        iu = 'placeholder'
        ip = 'placeholder'
    parser['TSDB'] = {'address': address, 'auth': ia, 'user': iu, 'pass': ip, 'database': idb, 'tsdtype': 'InfluxDB'}

if conf_tsdb_type == 'InfluxDB2':
    address = input('Please enter InfluxDBv2 address, defaults to http://127.0.0.1:8086: ')
    if address == '':
        address = 'http://127.0.0.1:8086'
    idb = input('What is your InfluxDBv2 bucket: ')
    org = input('What is your InfluxDBv2 org name: ')
    token = input('What is your InfluxDBv2 token: ')
    parser['TSDB'] = {'address': address, 'bucket': idb, 'token': token, 'organization': org, 'tsdtype': 'InfluxDB2'}

if conf_tsdb_type == 'OpenTSDB':
    address = input('Please enter OpenTSDB address, defaults to http://127.0.0.1:4242: ')
    if address == '':
        address = 'http://127.0.0.1:4242'
    oauth = input('Have you enabled authentication in OpenTSDB ? (yes/no): ')
    if oauth.lower() == 'yes':
        oa = 'True'
        ou = input('Username for OpenTSDB: ')
        op = input('Password for OpenTSDB: ')
    elif oauth.lower() == 'no':
        oa = 'False'
        ou = 'placeholder'
        op = 'placeholder'
    else:
        print('Your input was wrong, will disable OpenTSDB authentication in config: ')
        oa = 'False'
        ou = 'placeholder'
        op = 'placeholder'
    parser['TSDB'] = {'address': address, 'datapoints': '/api/put', 'auth': oa, 'user': ou, 'pass': op, 'tsdtype': 'OpenTSDB'}

if conf_tsdb_type == 'KairosDB':
    address = input('Please enter KairosDB address, defaults to http://127.0.0.1:8080: ')
    if address == '':
        address = 'http://127.0.0.1:8080'
    kauth = input('Have you enabled authentication in KairosDB ? (yes/no): ')
    if kauth.lower() == 'yes':
        ka = 'True'
        ku = input('Username for KairosDB: ')
        kp = input('Password for KairosDB: ')
    elif kauth.lower() == 'no':
        ka = 'False'
        ku = 'placeholder'
        kp = 'placeholder'
    else:
        print('Your input was wrong, will disable KairosDB authentication in config: ')
        ka = 'False'
        ku = 'placeholder'
        kp = 'placeholder'
    parser['TSDB'] = {'address': address, 'datapoints': '/api/v1/datapoints', 'auth': ka, 'user': ku, 'pass': kp,'tsdtype': 'KairosDB'}

if conf_tsdb_type == 'Carbon':
    address = input('Please enter Carbon address, defaults to http://127.0.0.1:2004: ')
    if address == '':
        address = 'http://127.0.0.1:2004'
    kauth = input('Have you enabled authentication in Carbon ? (yes/no): ')
    if kauth.lower() == 'yes':
        ca = 'True'
        cu = input('Username for Carbon: ')
        cp = input('Password for Carbon: ')
    elif kauth.lower() == 'no':
        ca = 'False'
        cu = 'placeholder'
        cp = 'placeholder'
    else:
        print('Your input was wrong, will disable Carbon authentication in config: ')
        ca = 'False'
        cu = 'placeholder'
        cp = 'placeholder'
    parser['TSDB'] = {'address': address,  'auth': ca, 'user': cu, 'pass': cp, 'tsdtype': 'Carbon'}

parser['SelfConfig'] = {'check_period_seconds': check_period, 'error_handler': '2', 'log_file': log_file, 'log_rotate_seconds': 3600, 'log_rotate_backups': 24,
                        'pid_file': pid_file,'cluster_name': cluster_name, 'host_group': host_group, 'tmpdir': tmpdir,
                        'debug_log': 'False', 'run_user': run_user, 'max_cache': '50000', 'location': location, 'shorthostname': shorthosts}

sparser['Unit'] = {'Description': 'PuyPuy Service', 'After': 'syslog.target'}
sparser['Install'] = {'WantedBy': 'multi-user.target'}

groups = [g.gr_name for g in grp.getgrall() if run_user in g.gr_mem]
gid = pwd.getpwnam(run_user).pw_gid
group = grp.getgrgid(gid).gr_name

sparser['Service'] = {'Type': 'simple', 'User': run_user, 'Group': group, 'WorkingDirectory': base_dir + '/',
                      'ExecStart': sys.executable + ' ' + base_dir + '/puypuy.py systemd', 'PIDFile': pid_file, 'Restart': 'on-failure'}


with open(service_file, 'w') as servicefile:
 sparser.write(servicefile)

with open(config_file, 'w') as configfile:
 parser.write(configfile)

src = (os.path.dirname(os.path.realpath("__file__"))+'/checks_available')
dst = (os.path.dirname(os.path.realpath("__file__"))+'/checks_enabled')

os.chdir(dst)

syschecks = ('check_cpustats.py', 'check_disks.py', 'check_load_average.py', 'check_memory.py', 'check_network_bytes.py')

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


if systemd_service == 'yes':
    subprocess.Popen('systemctl daemon-reload', stdout=subprocess.PIPE, shell=True).communicate()
    subprocess.Popen('systemctl enable oe-agent.service', stdout=subprocess.PIPE, shell=True).communicate()
    subprocess.Popen('systemctl start oe-agent', stdout=subprocess.PIPE, shell=True).communicate()
    print(bcolors.OKGREEN + 'Autostart of oe-agent is enabled' + bcolors.OKGREEN)
elif systemd_service == 'no':
    print(bcolors.OKGREEN + ' ' + bcolors.OKGREEN)
    print(bcolors.OKGREEN + 'Will not run oe-agent on boot, please manually start it' + bcolors.OKGREEN)
    print(bcolors.OKGREEN + 'You can  install oe-agent systemd service later by running ' + base_dir +'/installservice.py ' + 'script' + bcolors.OKGREEN)
else:
    print(bcolors.FAIL + ' ' + bcolors.FAIL)
    print(bcolors.FAIL + 'Failed to add oe-agent to autostart' + bcolors.FAIL)

for root, dirs, files in os.walk(base_dir, topdown=False):
    for name in files:
        os.chown((os.path.join(root, name)), uid, gid)
    for name in dirs:
        os.chown((os.path.join(root, name)), uid, gid)
