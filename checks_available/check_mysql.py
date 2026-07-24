'''
This check requires Python MySQLDB or pymysql, On Debian like systems do
APT: apt-get install python-mysqldb, or apt-get install python-pymysql
PIP: pip install MySQL-python or pip install pymysql
'''

import lib.basecheck
import lib.getconfig
import lib.puylogger
import lib.record_rate
import ast


try:
    try:
        import mysql.connector as mysqldriver
        lib.puylogger.print_message(__name__ + ' Using MySQLdb to connect to MySQL server')
    except:
        import MySQLdb as mysqldriver
        lib.puylogger.print_message(__name__ + ' Using MySQLdb to connect to MySQL server')
except:
    try:
        import pymysql as mysqldriver
        lib.puylogger.print_message(__name__ + ' Using pymysql to connect to MySQL server')
    except:
        lib.puylogger.print_message(__name__ + ' Error : Cannot load MySQL module, please install MySQLdb or pymysql ')

mysql_host = lib.getconfig.getparam('MySQL', 'host')
mysql_user = lib.getconfig.getparam('MySQL', 'user')
mysql_pass = lib.getconfig.getparam('MySQL', 'pass')

advanced = lib.getconfig.getparam('MySQL', 'custom')
check_type = 'mysql'

if advanced:
    custom_querry = ast.literal_eval(lib.getconfig.getparam('MySQL', 'query'))


class Check(lib.basecheck.CheckBase):

    def precheck(self):
        try:
            db = mysqldriver.connect(host=mysql_host, user=mysql_user, passwd=mysql_pass, )
            cur = db.cursor()
            cur.execute("SHOW GLOBAL STATUS WHERE Variable_name='Connections'"
                        "OR Variable_name='Com_select' "
                        "OR Variable_name='Com_delete_multi' "
                        "OR Variable_name='Com_delete' "
                        "OR Variable_name='Com_insert' "
                        "OR Variable_name='Com_update' "
                        "OR Variable_name='Com_create_temporary_table' "
                        "OR Variable_name='Com_drop_temporary_table' "
                        "OR Variable_name LIKE 'Bytes_%' "
                        "OR Variable_name LIKE 'Con%' "
                        "OR Variable_name LIKE 'Innodb_row_lock%' "
                        "OR Variable_name='Queries' "
                        "OR Variable_name='Questions' "        
                        "OR Variable_name='Slow_queries' "
                        "OR Variable_name='Qcache_hits' "
                        "OR Variable_name='Open_files' "
                        "OR Variable_name='Max_used_connections' "
                        "OR Variable_name='Threads_connected' "
                        "OR Variable_name='Innodb_rows_deleted' "
                        "OR Variable_name='Innodb_rows_inserted' "
                        "OR Variable_name='Innodb_rows_read' "        
                        "OR Variable_name='Innodb_rows_updated' "
                        "OR Variable_name='Innodb_data_read' "
                        "OR Variable_name='Innodb_data_writes' "
                        "OR Variable_name='Innodb_data_fsyncs' "
                        "OR Variable_name='Rpl_transactions_multi_engine' "
                        "OR Variable_name='Slave_retried_transactions' "
                        "OR Variable_name='Transactions_gtid_foreign_engine' "
                        "OR Variable_name='Transactions_multi_engine' "
                        "OR Variable_name='Slave_connections' "
                        "OR Variable_name='Slaves_connected' "
                        "OR Variable_name='Innodb_buffer_pool_reads' "
                        "OR Variable_name='Innodb_buffer_pool_read_requests' "
                        "OR Variable_name='Innodb_buffer_pool_write_requests' "
                        "OR Variable_name='Innodb_deadlocks' "
            "")
            non_rate_metrics = ('Max_used_connections', 'Slow_queries', 'Open_files', 'Threads_connected', 'Slave_connections', 'Slaves_connected',
                                'Com_drop_temporary_table', 'Com_create_temporary_table', 'Innodb_deadlocks')
            transactions = ('Rpl_transactions_multi_engine', 'Slave_retried_transactions',
                            'Transactions_gtid_foreign_engine', 'Transactions_multi_engine')
            innodblocks = ('Innodb_row_lock_current_waits', 'Innodb_row_lock_time', 'Innodb_row_lock_time_avg',
                           'Innodb_row_lock_time_max', 'Innodb_row_lock_waits')
            conn_errors = ('Connection_errors_accept', 'Connection_errors_internal', 'Connection_errors_max_connections',
                           'Connection_errors_peer_address', 'Connection_errors_select', 'Connection_errors_tcpwrap')
            commands = ('Com_select', 'Com_delete_multi', 'Com_delete', 'Com_insert', 'Com_update')
            for row in cur.fetchall():
                mytype = row[0]
                myvalue = row[1]
                if mytype in transactions:
                    tag = mytype.lower().replace("_transactions_", "_").replace("_transactions", "").replace("transactions_", "")
                    self.local_vars.append({'name': 'mysql_transactions', 'timestamp': self.timestamp, 'value': myvalue, 'check_type': check_type, 'extra_tag': {'transaction': tag}})
                elif mytype in innodblocks:
                    tag = mytype.lower().replace("innodb_row_lock_", "")
                    self.local_vars.append({'name': 'mysql_innodb_row_lock', 'timestamp': self.timestamp, 'value': myvalue, 'check_type': check_type, 'extra_tag': {'error': tag}})
                elif mytype in conn_errors:
                    tag = mytype.lower().replace("connection_errors_", "")
                    self.local_vars.append({'name': 'mysql_connection_errors', 'timestamp': self.timestamp, 'value': myvalue, 'check_type': check_type, 'extra_tag': {'error': tag}})
                elif mytype in non_rate_metrics:
                    self.local_vars.append({'name': 'mysql_'+ mytype.lower(), 'timestamp': self.timestamp, 'value': myvalue, 'check_type': check_type, })
                elif mytype in commands:
                    tag = mytype.lower().replace("com_", "")
                    vrate = self.rate.record_value_rate('mysql_command' + mytype + tag, myvalue, self.timestamp)
                    self.local_vars.append({'name': 'mysql_command', 'timestamp': self.timestamp, 'value': vrate, 'check_type': check_type, 'extra_tag': {'com': tag}})
                else:
                    vrate = self.rate.record_value_rate('mysql_' + mytype, myvalue, self.timestamp)
                    self.local_vars.append({'name': 'mysql_' + mytype.lower(), 'timestamp': self.timestamp, 'value': vrate, 'check_type': check_type, 'chart_type': 'Rate'})
            if advanced:
                for i in custom_querry:
                    cr = db.cursor()
                    cr.execute(custom_querry[i])
                    for row in cr.fetchall():
                        name = str(row[0])
                        value = float(row[1])
                        self.local_vars.append({'name': 'mysql_custom_query', 'timestamp': self.timestamp, 'value': value, 'check_type': check_type, 'extra_tag': {'name': name}})
            cur.close()
            db.close()
        except Exception as e:
            lib.puylogger.print_message(__name__ + ' Error : ' + str(e))
            pass

