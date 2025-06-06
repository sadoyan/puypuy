import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

metrics = lib.getconfig.getparam('Cotrun', 'metrics')
# metrics = 'http://127.0.0.1:9641/metrics'
check_type = 'coturn'
reaction = 0

meters = [
            'turn_traffic_sentb', 'turn_traffic_peer_sentb', 'turn_total_traffic_rcvb', 'turn_total_traffic_peer_sentb', 'process_open_fds', 'turn_traffic_peer_sentp',
            'turn_total_traffic_sentb', 'turn_traffic_rcvp', 'turn_traffic_peer_rcvb', 'turn_total_traffic_peer_sentb', 'stun_binding_request', 'turn_total_traffic_rcvp',
            'process_virtual_memory_bytes'
         ]

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            for c in data:
                if any(x in c for x in meters) and '#' not in c:
                    o = re.split(r'[{|} \s]+', c.replace('"', ''))
                    if len(o) > 2:
                        tags = o[1].replace('"', '').split('=')
                        value = self.rate.record_value_rate(o[0], o[-1], self.timestamp)
                        self.local_vars.append({'name': 'coturn_'+o[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type,
                             'extra_tag': {tags[0]: tags[-1]}})
                        # lib.puylogger.print_message({'name': 'coturn_'+o[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type,
                        #      'extra_tag': {tags[0]: tags[-1]}})
                    else:
                        if o[0] == 'process_open_fds' or o[0] == 'process_virtual_memory_bytes':
                            self.local_vars.append({'name': 'coturn_'+o[0], 'timestamp': self.timestamp, 'value': o[-1], 'reaction': reaction, 'check_type': check_type, })
                            # lib.puylogger.print_message({'name': 'coturn_' + o[0], 'timestamp': self.timestamp, 'value': o[-1], 'reaction': reaction, 'check_type': check_type, })
                        else:
                            value = self.rate.record_value_rate(o[0], o[-1], self.timestamp)
                            self.local_vars.append({'name': 'coturn_'+o[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type,})
                            # lib.puylogger.print_message({'name': 'coturn_' + o[0], 'timestamp': self.timestamp, 'value': value, 'reaction': reaction, 'check_type': check_type, })
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
