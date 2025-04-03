import lib.record_rate
import lib.getconfig
import lib.commonclient
import lib.puylogger
import lib.basecheck
import json

redis_host = lib.getconfig.getparam('Twemproxy', 'host')
redis_port = int(lib.getconfig.getparam('Twemproxy', 'port'))
check_type = 'twemproxy'

buffer_size = 4096
m1 = ''

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            ratedmetrics = {"requests", "request_bytes", "responses", "response_bytes"}
            rawmetrics = {"in_queue", "in_queue_bytes"}
            raw_data = json.loads(lib.commonclient.socketget(__name__, buffer_size, redis_host, redis_port, ''))
            # lib.puylogger.print_message(raw_data["curr_connections"])
            # lib.puylogger.print_message(raw_data["proxy"]["client_connections"])
            for k, v in raw_data["proxy"].items():
                if isinstance(v, dict):
                    for key, value in v.items():
                        if key in ratedmetrics:
                            reqrate = self.rate.record_value_rate('twemproxy_' + k + key, value, self.timestamp)
                            self.local_vars.append({'name': 'twemproxy_' + key, 'timestamp': self.timestamp, 'value': reqrate, 'check_type': check_type, 'extra_tag': {'backend': k}})
                        elif key in rawmetrics:
                            self.local_vars.append({'name': 'twemproxy_' + key, 'timestamp': self.timestamp, 'value': value, 'check_type': check_type, 'extra_tag': {'backend': k}})
            self.local_vars.append({'name': 'twemproxy_current_connections', 'timestamp': self.timestamp, 'value': raw_data["curr_connections"], 'check_type': check_type})
            self.local_vars.append({'name': 'twemproxy_client_connections', 'timestamp': self.timestamp, 'value': raw_data["proxy"]["client_connections"], 'check_type': check_type})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass