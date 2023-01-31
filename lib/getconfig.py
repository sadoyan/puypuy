import os
import configparser
import glob

config = configparser.RawConfigParser()
config_files = (glob.glob(os.getcwd()+'/conf/*.ini'))
config.read(config_files)

def getparam(key, value):
    v = config.get(key, value)
    if v == 'True':
        v = True
    if v == 'False':
        return False
    else:
        return v

def getsection(section):
    o = config.options(section)
    return o

def getsectionitems(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1