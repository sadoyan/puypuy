import lib.record_rate
import lib.commonclient
import lib.getconfig
import lib.puylogger
import lib.basecheck
import re

check_type = 'influxdb'

metrics = lib.getconfig.getparam("InfluxDB2", "metrics")
special = ("http_api_requests_total")
qc = ("qc_requests_total")
greps = ("boltdb_reads_total", "boltdb_writes_total",
         "go_goroutines", "go_memstats_alloc_bytes", "go_memstats_heap_alloc_bytes",
         "go_memstats_heap_alloc_bytes", "go_memstats_heap_idle_bytes", "go_threads",
         "task_executor_promise_queue_usage", "task_executor_total_runs_active",
         "task_executor_workers_busy", "task_scheduler_current_execution",
         "task_scheduler_total_execute_failure", "task_scheduler_total_schedule_fails")
detailed = ("http_query_request_bytes", "http_query_request_count","http_query_response_bytes",
           "http_write_request_bytes","http_write_request_count", "http_write_response_bytes")
reaction = 0

class Check(lib.basecheck.CheckBase):
    def precheck(self):
        try:
            data = lib.commonclient.httpget(__name__, metrics).splitlines()
            for c in data:
                a = re.split("{|} ", c.replace('"', ""))
                b = a[0].split()
                if b[0] in greps :
                    self.local_vars.append({"name": "influxdb_" + b[0], "timestamp": self.timestamp, "value": float(b[-1]), 'check_type': check_type, "reaction": reaction})
                if a[0] in detailed:
                    extra = a[1].split(",")[-1].split("=")
                    self.local_vars.append({"name": "influxdb_" + a[0], "timestamp": self.timestamp, "value": float(a[-1]),'check_type': check_type, "reaction": reaction, 'extra_tag':{extra[0]: extra[1]}})
        except Exception as e:
            lib.puylogger.print_message(__name__ + " Error : " + str(e))
            pass


