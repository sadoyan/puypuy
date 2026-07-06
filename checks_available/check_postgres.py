from psycopg2.extras import RealDictCursor

import lib.basecheck
import lib.getconfig
import lib.puylogger
import lib.record_rate

import psycopg2

host = lib.getconfig.getparam('Postgres', 'host')
user = lib.getconfig.getparam('Postgres', 'user')
pasw = lib.getconfig.getparam('Postgres', 'pass')
check_type = 'psql'

rate_list = ("xact_commit", "xact_rollback", "blks_read", "blks_hit",
            "tup_returned", "tup_fetched", "tup_inserted", "tup_updated", "tup_deleted",
            "temp_files", "temp_bytes", "deadlocks", "conflicts", "checksum_failures")
the_list = ("numbackends")
class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            db = psycopg2.connect(host=host, database="postgres",user=user, password=pasw)
            cur = db.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM pg_stat_database")
            for row in cur.fetchall():
                requests = row["xact_commit"] + row["xact_rollback"]
                if requests > 0:
                    reqrate = self.rate.record_value_rate('psql_requests_rate'+row["datname"], requests, self.timestamp)
                    self.local_vars.append({'name': 'psql_requests_rate', 'timestamp': self.timestamp, 'value': reqrate, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                try:
                    rbrate = row["xact_rollback"] / (row["xact_commit"] + row["xact_rollback"])
                    self.local_vars.append({'name': 'psql_rollback_ratio', 'timestamp': self.timestamp, 'value': rbrate, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                except:
                    pass
                try:
                    cache_hits = row["blks_hit"] / (row["blks_hit"] + row["blks_read"])
                    self.local_vars.append({'name': 'psql_cache_hits_ratio', 'timestamp': self.timestamp, 'value': cache_hits, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                except:
                    pass
                try:
                    write_amplification = row["tup_inserted"] + row["tup_updated"] + row["tup_deleted"]
                    if write_amplification > 0:
                        reqrate = self.rate.record_value_rate('write_amplification'+row["datname"], write_amplification, self.timestamp)
                        self.local_vars.append({'name': 'psql_write_ops', 'timestamp': self.timestamp, 'value': reqrate, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                except:
                    pass
                self.local_vars.append({'name': 'psql_numbackends', 'timestamp': self.timestamp, 'value': row["numbackends"], 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                for key, value in row.items():
                    if key in the_list:
                        if value > 0:
                            reqrate = self.rate.record_value_rate('psql_'+ key, value, self.timestamp)
                            self.local_vars.append({'name': 'psql_'+ key, 'timestamp': self.timestamp, 'value': reqrate, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
                        else:
                            self.local_vars.append({'name': 'psql_' + key, 'timestamp': self.timestamp, 'value': 0, 'check_type': check_type, 'extra_tag': {'dbname': row["datname"]}})
            cur.close()
            db.close()
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass

