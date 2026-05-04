import lib.record_rate
import lib.getconfig
import lib.commonclient
import lib.puylogger
import lib.basecheck


redis_host = lib.getconfig.getparam('Redis', 'host')
redis_port = int(lib.getconfig.getparam('Redis', 'port'))
redis_auth = str(lib.getconfig.getparam('Redis', 'auth'))
cpu_stats = str(lib.getconfig.getparam('Redis', 'cpustats'))
check_type = 'redis'

buffer_size = 4096
m1 = 'INFO\r\n'
m2 = 'auth ' + redis_auth + ' \r\n '

if redis_auth == 'False':
    message = m1
else:
    message = m2 + m1

cpustats = ['used_cpu_sys', 'used_cpu_user', 'used_cpu_sys_children', 'used_cpu_user_children', 'used_cpu_sys_main_thread', 'used_cpu_user_main_thread']

class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            raw_data = lib.commonclient.socketget(__name__, buffer_size, redis_host, redis_port, message)
            ms = ['connected_clients', 'used_memory', 'used_memory_rss', 'used_memory_peak','uptime_in_seconds','mem_fragmentation_ratio',
                'rdb_changes_since_last_save', 'rdb_bgsave_in_progress', 'rdb_last_bgsave_time_sec', 'rdb_current_bgsave_time_sec']
            if cpu_stats:
                for c in cpustats:
                    lib.puylogger.print_message(c)
                    ms.append(c)
            ms_rated = ('total_commands_processed', 'expired_keys', 'evicted_keys','keyspace_hits', 'keyspace_misses',
                        'total_net_input_bytes', 'total_net_output_bytes', 'total_reads_processed', 'total_writes_processed',
                        'io_threaded_total_prefetch_batches', 'io_threaded_total_prefetch_entries')
            datadict = {}
            for line in raw_data.splitlines():
                if line.startswith('db'):
                    line2 = line.split(":")
                    db=line2[0].strip()
                    for item in line2[1].split(","):
                        key, value = item.split("=")
                        self.local_vars.append({'name': 'redis_' + key, 'timestamp': self.timestamp, 'value': value, 'check_type': check_type, 'extra_tag':{'db': db}})
                elif ':' in line:
                    line2 = line.split(":")
                    datadict.update({line2[0]: line2[1]})

            for key, value in list(datadict.items()):
                if key in ms:
                    try:
                        value = int(value)
                    except:
                        pass
                    self.local_vars.append({'name': 'redis_' + key, 'timestamp': self.timestamp, 'value': value, 'check_type': check_type})
                if key in ms_rated:
                    vrate = self.rate.record_value_rate('redis_' + key , value, self.timestamp)
                    self.local_vars.append({'name':'redis_' + key, 'timestamp': self.timestamp, 'value': vrate, 'check_type': check_type, 'chart_type': 'Rate'})

        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
