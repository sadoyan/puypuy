#!/usr/bin/env bash
### BEGIN INIT INFO
# Provides: puypuy.sh
# Required-Start: $local_fs $network
# Should-Start: ypbind nscd ldap ntpd xntpd
# Required-Stop: $network
# Default-Start:  2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: start and stop TSD Client
# Description: TSD Client
### END INIT INFO#

# apt-get install  python-setproctitle

SCRIPT_DIR="$(cd $(dirname $0) && pwd)"
PYTHON=`which python3`
cd $SCRIPT_DIR
#RUNUSER=pastor

function getValue {
    VALUE=`grep $1 conf/config.ini|  awk '{print $NF}'`
    if [ `echo $VALUE  | grep -o ':'` ] ; then VALUE=`echo $VALUE| cut -d ':' -f2` ; fi
    if [ `echo $VALUE  | grep -o '='` ] ; then VALUE=`echo $VALUE| cut -d '=' -f2` ; fi
    echo $VALUE
}

RUNUSER=`getValue puypuy_user`
TMPDIR=`getValue tmpdir`
PIDFILE=`getValue pid_file`

    case "$1" in

    start)
    if [ ! -d  $TMPDIR ];
        then
            mkdir $TMPDIR
            chown $RUNUSER $TMPDIR
            chmod 755 $TMPDIR
    fi
    su $RUNUSER -s /bin/bash -c "$PYTHON puypuy.py start"
    ;;

    stop)
    su $RUNUSER -s /bin/bash -c "$PYTHON puypuy.py stop"
    rm -f checks_enabled/*.pyc
    ;;

    restart)
    $0 stop
    while [ -f  $PIDFILE ];
        do
            echo -n '.'
            sleep 1
        done
        echo
    $0 start
    ;;
    *)
    echo "Usage: `basename $0` start | stop | restart"
    ;;

    esac
