import lib
import json
from subprocess import Popen, PIPE


cfgs = lib.getconfig.getsection('Nagios')
nagcfgs = {}

for cfg in cfgs:
    nagcfgs[cfg] = lib.getconfig.getparam('Nagios', cfg)

def run_nag(name):
    try:
        input = json.loads(name)
    except Exception as e:
        print(e)
        return e
    if len(input) == 1:
        for key, val in input.items() :
            try:
                if val =="":
                    command = nagcfgs[key].split()
                else:
                    command=[nagcfgs[key].split()[0]]
                    for param in val.split():
                        command.append(param)
                p = Popen(command, stdout=PIPE)
                (output, err) = p.communicate()
                exit_code = p.wait()
                health_message = output.decode("utf-8").replace('\n', '')

                if exit_code == 0:
                    return json.dumps({'OK': health_message})
                if exit_code == 1:
                    return json.dumps({'WARNING': health_message})
                else:
                    return json.dumps({'CRITICAL': health_message})
            except Exception as e:
                print(e)
                return ("Somethinbg is worry")
