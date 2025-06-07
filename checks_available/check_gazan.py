import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

metrics = lib.getconfig.getparam('Gazan', 'metrics')
# metrics = "http://127.0.0.1:3000/metrics"
check_type = 'gazan'
greps = ('sum', 'count', 'process')
reaction = 0

rated = {'gazan_requests_by_method_total', 'gazan_requests_total', 'gazan_responses_total', 'gazan_requests_by_version_total'}
mat = {'gazan_request_latency_seconds_bucket', 'gazan_response_latency_seconds_bucket'}

class Check(lib.basecheck.CheckBase):
    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            request = { }
            response = {}
            for c in data:
                if '#' not in c:
                    a = re.split(r'[{|} \s]+', c.replace('"', ''))
                    if len(a) > 2:
                        d = dict(x.split("=") for x in a[1].split(","))
                        if a[0] in rated:
                            for k, v in d.items():
                                value = self.rate.record_value_rate(a[0]+k+v, a[-1], self.timestamp)
                                name = a[0].replace("_total", "")
                                self.local_vars.append({'name': name, 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type,'extra_tag': {k: v}})
                        elif a[0] == "gazan_request_latency_seconds_bucket":
                            for k, v in d.items():
                                request[v] = float(a[-1])
                        elif a[0] == "gazan_response_latency_seconds_bucket":
                            for k, v in d.items():
                                response[v] = float(a[-1])
                        else:
                            for k,v in d.items():
                                self.local_vars.append({'name': a[0], 'timestamp': self.timestamp, 'value': a[-1], 'reaction': reaction, 'check_type': check_type,'extra_tag': {k: v}})
                    else:
                        if a[0] in rated:
                            value = self.rate.record_value_rate(a[0], a[-1], self.timestamp)
                            name = a[0].replace("_total", "")
                            self.local_vars.append({'name': name, 'timestamp': self.timestamp, 'value': value, 'reaction': reaction})
                        else:
                            self.local_vars.append({'name': a[0], 'timestamp': self.timestamp, 'value': a[-1], 'reaction': reaction})
            # result = histogram_quantile(0.95, buckets)
            for x in [0.50, 0.75, 0.85, 0.90, 0.95, 0.99]:
                value = histogram_quantile(x, request)
                n = "percentile"
                v = str(int(x*100))
                self.local_vars.append({'name': "gazan_request_latency", 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type, 'extra_tag': {n: v}})
            for x in [0.50, 0.75, 0.85, 0.90, 0.95, 0.99]:
                value = histogram_quantile(x, response)
                n = "percentile"
                v = str(int(x*100))
                self.local_vars.append({'name': "gazan_response_latency", 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type, 'extra_tag': {n: v}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass


def histogram_quantile(q, buckets):
    sorted_buckets = sorted((float(k), v) for k, v in buckets.items())
    total = sorted_buckets[-1][1]
    if total == 0:
        return None
    target = q * total
    prev_le = 0.0
    prev_count = 0.0

    for le, count in sorted_buckets:
        if count >= target:
            delta_count = count - prev_count
            delta_le = le - prev_le
            if delta_count == 0:
                return le
            return prev_le + ((target - prev_count) / delta_count) * delta_le
        prev_le = le
        prev_count = count
    return sorted_buckets[-1][0]  # fallback (shouldn't hit normally)
