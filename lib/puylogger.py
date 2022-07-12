# import logging
import time
import lib.getconfig
# import os
# import gzip

import logging.handlers

cluster_name = lib.getconfig.getparam('SelfConfig', 'cluster_name')
host_group = lib.getconfig.getparam('SelfConfig', 'host_group')
debug_log = lib.getconfig.getparam('SelfConfig', 'debug_log')
tsdb_type = lib.getconfig.getparam('TSDB', 'tsdtype')
log_file = lib.getconfig.getparam('SelfConfig', 'log_file')
backupcount = int(lib.getconfig.getparam('SelfConfig', 'log_rotate_backups'))
seconds = int(lib.getconfig.getparam('SelfConfig', 'log_rotate_seconds'))

# def print_message(message):
#     logger = logging.getLogger("PuyPuy")
#     logger.setLevel(logging.INFO)
#     logging.basicConfig(filename=log_file, level=logging.INFO)
#     logging.info(str(time.strftime(" [%F %H %M:%S] ")) + message)


# class GZipRotator:
#     def __call__(self, source, dest):
#         os.rename(source, dest)
#         f_in = open(dest, 'rb')
#         f_out = gzip.open("%s.gz" % dest, 'wb')
#         f_out.writelines(f_in)
#         f_out.close()
#         f_in.close()
#         os.remove(dest)

log = logging.handlers.TimedRotatingFileHandler(log_file, 's', seconds, backupCount=backupcount)
log.setLevel(logging.INFO)
# log.rotator = GZipRotator()
logger = logging.getLogger('main')
logger.addHandler(log)
logger.setLevel(logging.INFO)
logger.propagate = False

def print_message(*args):
    mssg = str(args[0])
    if len(args) >= 1:
        for arg in args[1:]:
            mssg = str(mssg) + " " + str(arg)
    logger.info(str(time.strftime("[%F %H %M:%S] ")) + mssg)

# def print_message(message):
#     mssg = str(time.strftime("[%F %H %M:%S] ")) + message
#     logger.info(mssg)

def print_raw_message(message):
    logger.info(message)
