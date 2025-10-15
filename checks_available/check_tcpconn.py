import lib.record_rate
import lib.getconfig
import lib.basecheck
import lib.puylogger
check_type = 'system'

reaction = -3

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            to = []
            yoyo = {}
            files = ['/proc/net/tcp', '/proc/net/tcp6']
            for file in files:
                with open(file) as f:
                    lineno = 0
                    sockets = []
                    for line in f:
                        lineno += 1
                        if lineno == 1:
                            continue
                        ln = line.strip()
                        sockets.append(ln)
                f.close()

                for t in sockets:
                    to.append((t.split()[3]))

                enums = {
                    '01': 'established', '02': 'syn_sent', '03': 'syn_recv', '04': 'syn_recv',
                    '05': 'fin_wait1', '06': 'fin_wait2', '07': 'time_wait',
                    '08': 'close', '09': 'close_wait', '0A': 'last_ack',
                    '0B': 'listen', '0C': 'closing', '0D': 'new_syn_recv', '0E': 'max_states'
                }

                flags = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B', '0C', '0D', '0E')
                for u in flags:
                    yoyo[u.replace(u, enums[u])] = yoyo.get(u.replace(u, enums[u]), 0) + to.count(u)
            for k,v in yoyo.items():
                self.local_vars.append({'name': 'tcp_connections', 'timestamp': self.timestamp, 'value': v, 'check_type': check_type, 'extra_tag':{'flag': k}})

            ufiles = ['/proc/net/udp', '/proc/net/udp6']
            unum = 0
            for ufile in ufiles:
                unum = unum + sum(1 for _ in open(ufile))
            self.local_vars.append({'name': 'udp_clients', 'timestamp': self.timestamp, 'value': unum, 'check_type': check_type, 'extra_tag':{'flag': "udp"}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass

