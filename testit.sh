#!/bin/bash 

   case "$1" in

    oddeye)
	rm   /tmp/oddeye_tmp/* 
	./oddeye.sh start 
	sleep 3 
	./oddeye.sh stop 
	for  X in `ls /tmp/oddeye_tmp/`; 
	 do cat /tmp/oddeye_tmp/$X | cut -d '=' -f 3 | python -mjson.tool |ccze -A ; 
	echo '-------------------------------------------------------------------------------------------------------------------------------'
	done 
    ;;

    influx)
	rm   /tmp/oddeye_tmp/* 
	./oddeye.sh start 
	sleep 3 
	./oddeye.sh stop 
	for  X in `ls /tmp/oddeye_tmp/`; 
	 do cat /tmp/oddeye_tmp/$X |ccze -A ; 
	done 
    ;;

    bobo)
	echo bobo
    ;;
    *)
    echo "Usage: `basename $0` start | stop | restart"
    ;;

    esac




