import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

metrics = lib.getconfig.getparam('Traefik', 'metrics')
check_type = 'traefik'
greps = ('sum', 'count', 'process')
reaction = 0

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            totals = 0
            for c in data:
                if c.startswith('traefik_service_requests_total'):
                    a = re.split('{|} ', c.replace('"', ''))
                    totals = totals + float(a[-1])

                if any(x in c for x in greps) and '#' not in c:
                    a = re.split('{|} ', c.replace('"', ''))
                    if c.startswith('traefik_'):
                        s = dict(item.split("=") for item in a[1].split(","))
                        self.local_vars.append({'name': a[0].replace('request', s['protocol'].split()[0]),
                                                'timestamp': self.timestamp,
                                                'value': a[2],
                                                'reaction': -3,
                                                'extra_tag': {'status_code': s['code']}})
                    else:
                        self.local_vars.append({'name': 'traefik_' + a[0].split()[0], 'timestamp': self.timestamp, 'value': float(a[0].split()[1]), 'reaction': reaction})
            reqrate = self.rate.record_value_rate('traefik_requests', totals, self.timestamp)
            self.local_vars.append({'name': 'traefik_totalrequests', 'timestamp': self.timestamp, 'value': reqrate, 'reaction': reaction})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass


