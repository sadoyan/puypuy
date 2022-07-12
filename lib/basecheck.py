import lib.record_rate
import lib.getconfig
import lib.pushdata
import lib.puylogger
import datetime


class CheckBase:
    check_type = 'base'
    values_type = 'none'
    local_vars = []
    rate = lib.record_rate.ValueRate()
    last = lib.record_rate.GetPrevValue()
    jsondata = lib.pushdata.JonSon()
    metrics = []

    def __init__(self):
        self.cluster_name = lib.getconfig.getparam('SelfConfig', 'cluster_name')
        self.host_group = lib.getconfig.getparam('SelfConfig', 'host_group')
        self.location = lib.getconfig.getparam('SelfConfig', 'location')
        self.error_handler = int(lib.getconfig.getparam('SelfConfig', 'error_handler'))
        self.timestamp = int(datetime.datetime.now().strftime("%s"))
        # self.debug_info = lib.getconfig.getparam('SelfConfig', 'print_info')

    def info(self):
        for t in self.local_vars:
            lib.puylogger.print_raw_message(self.__module__ + ' : ' + str(t))

    def precheck(self):
        pass

    def runcheck(self):
        self.local_vars = []
        self.precheck()
        # if self.debug_info is True:
        #     self.info()
        for k in self.local_vars:
            if 'host' not in k:
                k['host'] = lib.pushdata.hostname
        return self.local_vars

