import pycurl
import socket
import lib.puylogger
import lib.pushdata
from io import BytesIO

def httpget(name, url, auth=None, headers=None):
    try:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FAILONERROR, True)
        c.setopt(pycurl.CONNECTTIMEOUT, 10)
        c.setopt(pycurl.USERAGENT, 'OddEye.co (Python agent)')
        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.NOSIGNAL, 5)
        if auth is not None:
            c.setopt(pycurl.USERPWD, auth)
        if headers is not None:
            c.setopt(pycurl.HTTPHEADER, [headers])
        c.perform()
        c.close()
        body = buffer.getvalue()
        return body.decode('iso-8859-1')
    except Exception as err:
        if name == 'check_oddeye':
            lib.pushdata.print_error(name, err)
        else:
            lib.puylogger.print_message(name + ' ' + str(err))
            lib.pushdata.print_error(name, err)


def socketget(name, buff, host, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        s.send(message.encode())
        raw_data = s.recv(buff).decode()
        s.close()
        return raw_data
    except Exception as err:
        lib.puylogger.print_message(name + ' ' + str(err))
        lib.pushdata.print_error(name, err)

