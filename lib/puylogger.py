import time
import lib.getconfig

import logging.handlers

cluster_name = lib.getconfig.getparam('SelfConfig', 'cluster_name')
host_group = lib.getconfig.getparam('SelfConfig', 'host_group')
debug_log = lib.getconfig.getparam('SelfConfig', 'debug_log')
tsdb_type = lib.getconfig.getparam('TSDB', 'tsdtype')
log_file = lib.getconfig.getparam('SelfConfig', 'log_file')
backupcount = int(lib.getconfig.getparam('SelfConfig', 'log_rotate_backups'))
seconds = int(lib.getconfig.getparam('SelfConfig', 'log_rotate_seconds'))


log = logging.handlers.TimedRotatingFileHandler(log_file, 's', seconds, backupCount=backupcount)
log.setLevel(logging.INFO)
logger = logging.getLogger('main')
logger.addHandler(log)
logger.setLevel(logging.INFO)
logger.propagate = False

def print_message(*args):
    mssg = args[0]
    if len(args) >= 1:
        for arg in args[1:]:
            mssg = mssg + " " + str(arg)
    logger.info(str(time.strftime("[%F %H %M:%S] ")) + mssg)

def print_raw_message(message):
    logger.info(message)
