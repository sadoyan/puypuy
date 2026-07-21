import lib.getconfig
import lib.pushdata
import lib.basecheck
import lib.puylogger
warn_level = int(lib.getconfig.getparam('Load Average', 'high'))
crit_level = int(lib.getconfig.getparam('Load Average', 'severe'))
static_alerts = lib.getconfig.getparam('Load Average', 'static_enabled')

check_type = 'system'
reaction = -3

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        cpucount = 0
        procstats = open("/proc/stat", "r")
        for line in procstats:
            if 'cpu' in line:
                cpucount += 1
        cpucount -= 1
        procstats.close()

        try:
            loadavg = open("/proc/loadavg", "r")
            proc_loadavg = loadavg.readline().split()
            self.local_vars.append({'name': 'sys_load_1', 'timestamp': self.timestamp, 'value': proc_loadavg[0]})
            self.local_vars.append({'name': 'sys_load_5', 'timestamp': self.timestamp, 'value': proc_loadavg[1], 'reaction': reaction})
            self.local_vars.append({'name': 'sys_load_15', 'timestamp': self.timestamp, 'value': proc_loadavg[2], 'reaction': reaction})
            loadavg.close()
            uptime = open("/proc/uptime", "r")
            seconds = uptime.readline().split()
            self.local_vars.append({'name': 'uptime_seconds', 'timestamp': self.timestamp, 'value': seconds[0]})
            uptime.close()
        except Exception as e:
            lib.pushdata.print_error(__name__ , (e))
            pass