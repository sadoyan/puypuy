import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

# metrics = lib.getconfig.getparam('Traefik', 'metrics')
metrics = "http://g01:3000/metrics"
check_type = 'gazan'
greps = ('sum', 'count', 'process')
reaction = 0

rated = {'gazan_requests_by_method_total', 'gazan_requests_total', 'gazan_responses_total'}
mat = {'gazan_response_latency_seconds_count', 'gazan_response_latency_seconds_sum'}
class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            lat_mat = {}
            for c in data:
                if '#' not in c:
                    a = re.split(r'[{|} \s]+', c.replace('"', ''))
                    if len(a) > 2:
                        d = dict(x.split("=") for x in a[1].split(","))
                        if a[0] in rated:
                            for k, v in d.items():
                                value = self.rate.record_value_rate(a[0]+k+v, a[-1], self.timestamp)
                                lib.puylogger.print_message({'name': a[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type,'extra_tag': {k: v}})
                        else:
                            for k,v in d.items():
                                lib.puylogger.print_message({'name': a[0], 'timestamp': self.timestamp, 'value': a[-1], 'reaction': reaction, 'check_type': check_type,'extra_tag': {k: v}})
                    else:
                        if a[0] in mat:
                            lat_mat[a[0]]=float(a[-1])
                        if a[0] in rated:
                            value = self.rate.record_value_rate(a[0], a[-1], self.timestamp)
                            lib.puylogger.print_message(' ====== name', a[0], 'value', value, "======")
                            # lib.puylogger.print_message({'name': a[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction})
                        else:
                            lib.puylogger.print_message({'name': a[0], 'timestamp': self.timestamp, 'value': a[-1], 'reaction': reaction})
            lat = lat_mat['gazan_response_latency_seconds_sum']/lat_mat['gazan_response_latency_seconds_count']
            lib.puylogger.print_message({'name': "gazan_average_response_latency", 'timestamp': self.timestamp, 'value': round(lat, 5), 'reaction': reaction})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass


