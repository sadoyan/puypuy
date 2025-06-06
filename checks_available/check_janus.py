import lib.record_rate
import lib.commonclient
import lib.puylogger
import lib.getconfig
import lib.basecheck
import json

admin_url = lib.getconfig.getparam('Janus', 'adminapi')
secret = lib.getconfig.getparam('Janus', 'secret')
check_type = 'janus'
lsd = json.dumps({"janus": "list_sessions", "transaction": "abcd1234", "admin_secret": secret})

class Check(lib.basecheck.CheckBase):
    def precheck(self):
        try:
            sessions = json.loads(lib.commonclient.httppost(__name__, admin_url, None, None, lsd))["sessions"]
            # self.local_vars.append({'name': 'janus' + o.lower(), 'timestamp': self.timestamp, 'value': vle, 'check_type': check_type, 'reaction': -1, 'extra_tag': {'gctype': nme}})
            self.local_vars.append({'name': 'janus_sessions', 'timestamp': self.timestamp, 'value': len(sessions), 'check_type': check_type, 'reaction': 0})
            for session in sessions:
                payload = json.dumps({"janus": "list_handles", "session_id" : session, "transaction": "abcd1234", "admin_secret": secret })
                handles = json.loads(lib.commonclient.httppost(__name__, admin_url, None, None, payload))["handles"]
                self.local_vars.append({'name': 'janus_handlers', 'timestamp': self.timestamp, 'value': len(handles), 'check_type': check_type, 'reaction': 0, 'extra_tag': {'session': str(session)}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
