import lib.getconfig
import lib.pushdata
import lib.basecheck
import lib.puylogger
import os

check_type = "gauge"
configs = lib.getconfig.getsectionitems("Open Files")

class Check(lib.basecheck.CheckBase):
    def precheck(self):
        pids = {}
        try:
            for k, v in configs.items():
                p = open(v)
                pids["openfiles_" + k] = p.read().replace("\n", "")
                p.close()
            for k,v in pids.items():
                value = len(os.listdir("/proc/" + v + "/fd"))
                lib.puylogger.print_message(str({'name': k, 'timestamp': self.timestamp, 'value': str(value), 'check_type': check_type, }))
                # self.local_vars.append({'name': k, 'timestamp': self.timestamp, 'value': str(value), 'check_type': check_type,})
        except Exception as e:
            lib.pushdata.print_error(__name__ , (e))
            pass