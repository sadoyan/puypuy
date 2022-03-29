import lib.getconfig
import lib.pushdata
import lib.puylogger
import lib.record_rate
import lib.commonclient
import lib.basecheck
import json

host = lib.getconfig.getparam('ElasticSearch', 'host')
stats = lib.getconfig.getparam('ElasticSearch', 'stats')
tpstats = lib.getconfig.getparam('ElasticSearch', 'threadpoolstats')
elastic_url = host + stats
check_type = 'elasticsearch'
reaction = -3

if tpstats.lower() == 'yes':
    poolstats = True
else:
    poolstats = False


class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            stats_json = json.loads(lib.commonclient.httpget(__name__, elastic_url))
            node_keys = list(stats_json['nodes'].keys())[0]
            data = {}
            rated_stats = {}

            global_stats = host + '/_stats/docs,store'
            global_json = json.loads(lib.commonclient.httpget(__name__, global_stats))
            alldocs = global_json['_all']['primaries']['docs']['count']
            docsinrate = self.rate.record_value_rate('es_total_docs_in', alldocs, self.timestamp)
            self.local_vars.append({'name': 'elasticsearch_cluster_docs', 'timestamp': self.timestamp, 'value': alldocs, 'check_type': check_type})
            self.local_vars.append({'name': 'elasticsearch_cluster_ingest_rate', 'timestamp': self.timestamp, 'value': docsinrate, 'check_type': check_type})
            self.local_vars.append({'name': 'elasticsearch_cluster_shards', 'timestamp': self.timestamp, 'value': global_json['_shards']['total'], 'check_type': check_type})
            self.local_vars.append({'name': 'elasticsearch_cluster_storage_usage', 'timestamp': self.timestamp, 'value': global_json['_all']['total']['store']['size_in_bytes'], 'check_type': check_type})

            eshealth_status = host + '/_cluster/health'
            eshealth_json = json.loads(lib.commonclient.httpget(__name__, eshealth_status))

            status = eshealth_json['status']

            h1stats = {'cluster': eshealth_json['cluster_name'],
                       'status' : eshealth_json['status'],}
            h2stats = {'active_shards': eshealth_json['active_shards'],
                      'relocating_shards': eshealth_json['relocating_shards'],
                      'initializing_shards': eshealth_json['initializing_shards'],
                      'unassigned_shards': eshealth_json['unassigned_shards']
                      }

            eshealth_message = 'Cluster: ' + h1stats['cluster'] + \
                               ', Status: ' + h1stats['status'] + \
                               ', Shards Active: ' + str(h2stats['active_shards']) + \
                               ', Relocating: ' + str(h2stats['relocating_shards']) + \
                               ', Initializing: ' + str(h2stats['initializing_shards'])

            if status == 'green':
                health_value = 0
                err_type = 'OK'
            elif status == 'yellow':
                health_value = 9
                err_type = 'WARNING'
            else:
                health_value = 16
                err_type = 'ERROR'
            self.jsondata.send_special("ElasticSearch-Health", self.timestamp, health_value, eshealth_message, err_type)

            for k,v in h2stats.items():
                self.local_vars.append({'name': 'elasticsearch_' + k, 'timestamp': self.timestamp, 'value': v, 'check_type': check_type})

            rated_stats.update({''
                        'search_total':stats_json['nodes'][node_keys]['indices']['search']['query_total'],
                        'index_total':stats_json['nodes'][node_keys]['indices']['indexing']['index_total'],
                        'delete_total': stats_json['nodes'][node_keys]['indices']['indexing']['delete_total'],
                        'refresh_total':stats_json['nodes'][node_keys]['indices']['refresh']['total'],
                        'get_total':stats_json['nodes'][node_keys]['indices']['get']['total'],
                        'fetch_total':stats_json['nodes'][node_keys]['indices']['search']['fetch_total'],
                        'fetch_time':stats_json['nodes'][node_keys]['indices']['search']['fetch_time_in_millis'],
                        'index_time':stats_json['nodes'][node_keys]['indices']['indexing']['index_time_in_millis'],
                        'search_search_time':stats_json['nodes'][node_keys]['indices']['search']['query_time_in_millis'],
                        'merge_time':stats_json['nodes'][node_keys]['indices']['merges']['total_time_in_millis'],
                        'merge_docs':stats_json['nodes'][node_keys]['indices']['merges']['total_docs'],
                        'merge_size':stats_json['nodes'][node_keys]['indices']['merges']['total_size_in_bytes'],
                        'refresh_time':stats_json['nodes'][node_keys]['indices']['refresh']['total_time_in_millis'],
                        'query_cache_evictions':stats_json['nodes'][node_keys]['indices']['query_cache']['evictions'],
                        'query_cache_hit': stats_json['nodes'][node_keys]['indices']['query_cache']['hit_count'],
                        'query_cache_mis': stats_json['nodes'][node_keys]['indices']['query_cache']['miss_count'],
                        'get_time':stats_json['nodes'][node_keys]['indices']['get']['time_in_millis'],
                        'gc_old_count':stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['old']['collection_count'],
                        'gc_young_count':stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['young']['collection_count'],
                        })

            ogc_young_time_ms = stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['young']['collection_time_in_millis']
            ogc_old_time_ms = stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['old']['collection_time_in_millis']
            ogc_young_count = stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['young']['collection_count']
            ogc_old_count = stats_json['nodes'][node_keys]['jvm']['gc']['collectors']['old']['collection_count']

            ogc_young_time_ms_get_last = self.last.return_last_value('ogc_young_time_ms_get_last', ogc_young_time_ms)
            ogc_old_time_ms_get_last = self.last.return_last_value('ogc_old_time_ms', ogc_old_time_ms)
            ogc_young_count_get_last = self.last.return_last_value('ogc_young_count_get_last', ogc_young_count)
            ogc_old_count_get_last =  self.last.return_last_value('ogc_old_count_get_last', ogc_old_count)

            if ogc_young_time_ms > ogc_young_time_ms_get_last and ogc_young_count > ogc_young_count_get_last:
                value_y = float("{:.2f}".format((ogc_young_time_ms - ogc_young_time_ms_get_last) / (ogc_young_count - ogc_young_count_get_last)))
            else:
                value_y = 0.0
            self.local_vars.append({'name': 'elasticsearch_gc_young_time_ms', 'timestamp': self.timestamp, 'value': value_y, 'check_type': check_type})

            if ogc_old_time_ms > ogc_old_time_ms_get_last and ogc_old_count > ogc_old_count_get_last:
                value_o = float("{:.2f}".format((ogc_old_time_ms - ogc_old_time_ms_get_last) / (ogc_old_count - ogc_old_count_get_last)))
            else:
                value_o = 0.0

            self.local_vars.append({'name': 'elasticsearch_gc_old_time_ms', 'timestamp': self.timestamp, 'value': value_o, 'check_type': check_type})

            for key, value in list(rated_stats.items()):
                reqrate=self.rate.record_value_rate('es_'+key, value, self.timestamp)
                if reqrate >= 0:
                    self.local_vars.append({'name': 'elasticsearch_' + key, 'timestamp': self.timestamp, 'value': reqrate, 'check_type': check_type, 'chart_type': 'Rate'})
    
            data.update({''
                        'elasticsearch_heap_commited':stats_json['nodes'][node_keys]['jvm']['mem']['heap_committed_in_bytes'],
                        'elasticsearch_heap_used':stats_json['nodes'][node_keys]['jvm']['mem']['heap_used_in_bytes'],
                        'elasticsearch_non_heap_commited':stats_json['nodes'][node_keys]['jvm']['mem']['non_heap_committed_in_bytes'],
                        'elasticsearch_non_heap_used':stats_json['nodes'][node_keys]['jvm']['mem']['non_heap_used_in_bytes'],
                        'elasticsearch_open_files':stats_json['nodes'][node_keys]['process']['open_file_descriptors'],
                        'elasticsearch_http_connections':stats_json['nodes'][node_keys]['http']['current_open']
                         })
            for key, value in list(data.items()):
                if key == 'elasticsearch_non_heap_used' or key == 'elasticsearch_heap_used' or key == 'elasticsearch_non_heap_committed' or key == 'elasticsearch_heap_committed':
                    self.local_vars.append({'name': key, 'timestamp': self.timestamp, 'value': value, 'check_type': check_type, 'reaction': reaction})
                else:
                    self.local_vars.append({'name': key, 'timestamp': self.timestamp, 'value': value, 'check_type': check_type})
            if poolstats:
                for tp in stats_json['nodes'][node_keys]['thread_pool'].keys():
                    for name in ('active', 'queue'):
                        if name in stats_json['nodes'][node_keys]['thread_pool'][tp].keys():
                            self.local_vars.append(
                                {'name': 'elasticsearch_thread_pool', 'timestamp': self.timestamp,
                                 'value': stats_json['nodes'][node_keys]['thread_pool'][tp][name], 'check_type': name,
                                 'reaction': -3, 'extra_tag': {'pool': tp}})

        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass
