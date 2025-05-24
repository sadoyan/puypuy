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

SCRIPT_DIR="$(cd $(dirname $0) && pwd)"
PYTHON=`which python3`
cd $SCRIPT_DIR

function getValue {
    VALUE=`grep $1 conf/config.ini|  awk '{print $NF}'`
    if [ `echo $VALUE  | grep -o ':'` ] ; then VALUE=`echo $VALUE| cut -d ':' -f2` ; fi
    if [ `echo $VALUE  | grep -o '='` ] ; then VALUE=`echo $VALUE| cut -d '=' -f2` ; fi
    echo $VALUE
}

RUNUSER=`getValue run_user`
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

    systemd)
    if [ ! -d  $TMPDIR ];
        then
            mkdir $TMPDIR
            chown $RUNUSER $TMPDIR
            chmod 755 $TMPDIR
    fi
    su $RUNUSER -s /bin/bash -c "$PYTHON puypuy.py systemd"
    ;;


    stop)
    su $RUNUSER -s /bin/bash -c "$PYTHON puypuy.py stop"
    rm -f checks_enabled/*.pyc
    ;;

    restart)
    cd $SCRIPT_DIR && ./puypuy.sh stop
    while [ -f  $PIDFILE ];
        do
            echo -n '.'
            sleep 1
        done
        echo
    cd $SCRIPT_DIR && ./puypuy.sh start
    ;;
    price)
    cd lib
    su $RUNUSER -s /bin/bash -c "$PYTHON getprice.py"
    ;;

    *)
    echo "Usage: `basename $0` start | stop | restart| systemd | price"
    ;;

    esac
