import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

metrics = lib.getconfig.getparam('Scilla', 'stats')
check_type = 'scylladb'
reaction = 0

greps = [
        'scylla_node_operation_mode', 'scylla_reactor_utilization', 'scylla_transport_requests_served',
        'scylla_storage_proxy_coordinator_write_latency_count', 'scylla_storage_proxy_coordinator_write_latency_sum',
        'scylla_storage_proxy_coordinator_write_timeouts', 'scylla_storage_proxy_coordinator_read_latency_count',
        'scylla_storage_proxy_coordinator_read_latency_sum', 'scylla_storage_proxy_coordinator_read_timeouts', 'scylla_cache_row_hits', 'scylla_cache_row_misses',
        'scylla_cache_bytes_total', 'scylla_cache_bytes_used', 'scylla_cache_concurrent_misses_same_key',
        'scylla_sstables_row_reads', 'scylla_sstables_range_partition_reads', 'scylla_sstables_range_tombstone_writes', 'scylla_sstables_row_writes',
        'scylla_sstables_single_partition_reads', 'scylla_sstables_sstable_partition_reads', 'scylla_sstables_static_row_writes', 'scylla_sstables_tombstone_writes'
    ]

sgnames = {'main', 'statement', 'compaction'}

class Check(lib.basecheck.CheckBase):
    def precheck(self):
        try:
            tempo = {}
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            for c in data:
                if any(x in c for x in greps) and '#' not in c:
                    o = re.split('{|} ', c.replace('"', ''))
                    d = dict(x.split("=") for x in o[1].split(","))
                    if 'scheduling_group_name' in d.keys():
                        for sgname in sgnames:
                            if sgname in d.values():
                                if o[0] not in tempo.keys():
                                    tempo[o[0]] = {d['scheduling_group_name']: float(o[-1])}
                                elif d['scheduling_group_name'] not in tempo[o[0]].keys():
                                    tempo[o[0]][d['scheduling_group_name']] = float(o[-1])
                                else:
                                    tempo[o[0]][d['scheduling_group_name']] = tempo[o[0]][d['scheduling_group_name']] + float(o[-1])
                    else:
                        if o[0] not in tempo.keys():
                            tempo[o[0]] = float(o[-1])
                        else:
                            tempo[o[0]] = tempo[o[0]] + float(o[-1])

            for k, v in tempo.items():
                if type(v) is float:
                    self.local_vars.append({'name': k, 'timestamp': self.timestamp, 'value': v, 'reaction': reaction,  'check_type': check_type})
                else:
                    for kk, vv in v.items():
                        self.local_vars.append({'name': k, 'timestamp': self.timestamp, 'value': vv, 'reaction': reaction,  'check_type': check_type, 'extra_tag': {'scheduling_group': kk}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
