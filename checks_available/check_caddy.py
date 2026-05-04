import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

metrics = lib.getconfig.getparam('Caddy', 'metrics')
check_type = 'caddy'
rated = ('caddy_http_requests_total')
greps = ('go_gc_duration_seconds_sum', 'go_memstats_alloc_bytes_total',
         'go_memstats_alloc_bytes', 'go_memstats_heap_alloc_bytes', 'go_memstats_heap_objects')
reaction = 0

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            chrt = 0.0
            for c in data:
                a = re.split('{|} ', c.replace('"', ''))
                if a[0] in rated and 'remaining_auto_https_redirects' not in c:
                    reqrate = self.rate.record_value_rate(str(a[1]), float(a[-1]), self.timestamp)
                    chrt += reqrate
                elif a[0].split()[0] in greps and 'remaining_auto_https_redirects' not in c:
                    v = float(a[-1].split()[-1])
                    k = a[0].split()[0]
                    self.local_vars.append({'name': 'caddy_'+k, 'timestamp': self.timestamp, 'value':  round(v, 2), 'reaction': reaction})
            self.local_vars.append({'name': 'caddy_http_requests_total', 'timestamp': self.timestamp, 'value': chrt, 'reaction': reaction})
            # lib.puylogger.print_message({'name': 'caddy_http_requests_total', 'timestamp': self.timestamp, 'value': chrt, 'reaction': reaction})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass


