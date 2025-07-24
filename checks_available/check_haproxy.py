import json

import lib.record_rate
import lib.getconfig
import lib.commonclient
import lib.puylogger
import lib.basecheck
import csv
from io import StringIO

haproxy_url = lib.getconfig.getparam('HAProxy', 'url')
haproxy_auth = lib.getconfig.getparam('HAProxy', 'user')+':'+lib.getconfig.getparam('HAProxy', 'pass')
curl_auth = lib.getconfig.getparam('HAProxy', 'auth')
check_type = 'haproxy'

interested = {"rate", "rate_max", "req_rate",  "req_rate_max", "conn_rate", "conn_rate_max", "conn_tot","reuse", "cache_lookups", "cache_hits", }
class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            if curl_auth is True:
                t = lib.commonclient.httpget(__name__, haproxy_url, haproxy_auth)
            else:
                t = lib.commonclient.httpget(__name__, haproxy_url)

            reader = csv.DictReader(StringIO(t, newline='\n'), delimiter=',')
            for row in reader:
                if row["svname"] == "BACKEND":
                    for k,v in row.items():
                        if k in interested:
                            if v != "":
                                lib.puylogger.print_message({'name': 'haproxy_' + k, 'timestamp': self.timestamp, 'value': v, 'check_type': check_type, 'chart_type': 'Rate','extra_tag': {'appname': row["# pxname"]}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass