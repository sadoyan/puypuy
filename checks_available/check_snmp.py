import lib.getconfig
import lib.basecheck
import lib.puylogger
import configparser
import subprocess
import os
import glob


to = 2

config = configparser.RawConfigParser()
config_file = (glob.glob(os.getcwd()+'/../conf/snmp/*.ini'))
config.read(config_file)
reaction = 0

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            for netdev in config.sections():
                command = 'snmpget  -v3 '
                command = command + '-l ' + config.get(netdev, 'security_level') \
                          + ' -u ' + config.get(netdev, 'user_name') \
                          + ' -A ' + config.get(netdev, 'user_pass') \
                          + ' -X ' + config.get(netdev, 'privacy_pass') \
                          + ' -a ' + config.get(netdev, 'auth_protocol') \
                          + ' -x ' + config.get(netdev, 'privacy_protocol') \
                          + ' ' + config.get(netdev, 'server') \
                          + ':' + config.get(netdev, 'port')
                valueslist = ''
                valdict = {}
                for (each_key, each_val) in config.items(netdev):
                    if each_key.startswith('oid_'):
                        valdict[each_val] = each_key.replace('oid_', '')
                        valueslist = valueslist + ' ' + each_val
                c2 = command + ' ' + valueslist

                try:

                    p1 = subprocess.run(c2, stdout=subprocess.PIPE, shell=True, universal_newlines=True, timeout=to)
                    for x in p1.stdout.replace('iso.', '.1.').split('\n'):
                        if len(x) > 0:
                            a = x.split()
                            u = a[0]
                            self.local_vars.append({'name': 'snmp_' + valdict[u], 'timestamp': self.timestamp, 'value': a[-1], 'reaction': reaction, 'extra_tag': {'devicename': netdev}})

                except Exception as e:
                    lib.puylogger.print_message(__name__ + ' Error connecting to ' + ' '+ netdev )

        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
