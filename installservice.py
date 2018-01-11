#!/usr/bin/env python3

import configparser
import os
import pwd
import grp
import sys
import subprocess

base_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(base_dir)

config = configparser.RawConfigParser()
config_file = 'conf/config.ini'
systemd_file = '/lib/systemd/system/oe-agent.service'
config.read(config_file)

pid= config.get('SelfConfig', 'pid_file')
run_user = config.get('SelfConfig', 'run_user')
sparser = configparser.ConfigParser()
sparser.optionxform= str

sparser['Unit'] = {'Description': 'OddEye Agent Service', 'After': 'syslog.target'}
sparser['Install'] = {'WantedBy': 'multi-user.target'}

groups = [g.gr_name for g in grp.getgrall() if run_user in g.gr_mem]
gid = pwd.getpwnam(run_user).pw_gid
group = grp.getgrgid(gid).gr_name

sparser['Service'] = {'Type': 'simple', 'User': run_user, 'Group': group, 'WorkingDirectory': base_dir + '/',
                      'ExecStart': sys.executable + ' ' + base_dir + '/oddeye.py  start', 'PIDFile': pid}

with open(systemd_file, 'w') as servicefile:
 sparser.write(servicefile)

subprocess.Popen('systemctl daemon-reload', stdout=subprocess.PIPE, shell=True).communicate()
subprocess.Popen('systemctl enable oe-agent.service', stdout=subprocess.PIPE, shell=True).communicate()
subprocess.Popen('systemctl start oe-agent', stdout=subprocess.PIPE, shell=True).communicate()
