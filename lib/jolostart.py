import urllib.request, urllib.error, urllib.parse
import os
import subprocess
import time
# p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
jarfile = os.path.dirname(os.path.realpath("__file__")) + '/../lib/agent.jar'

def do_joloikia(java,juser,jclass,jmx_url):
    port = jmx_url.split(':')[2].split('/')[0]
    ps = subprocess.Popen(['sudo', '-u', juser, java, '-jar', jarfile, 'list'], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].split('\n')
    jpid = [s for s in ps if jclass in s][0].split()[0]
    def jolostart():
        os.system('sudo -u ' + juser + ' ' + java + ' -jar ' + jarfile + ' --port ' + port + ' --agentContext /puypuy/ start ' + str(jpid) +  ' > /dev/null  2>&1')
    jolostart()
    time.sleep(1)
    try:
        if urllib.request.urlopen(jmx_url).getcode() is not 200:
            jolostart()
    except:
        jolostart()
