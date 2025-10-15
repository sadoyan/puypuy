import lib.getconfig
from http.server import BaseHTTPRequestHandler, HTTPServer
import lib.getconfig
import lib.nag
import lib.puylogger
import lib.pushdata
import socket

ws = lib.getconfig.getparam('WebServer', 'webserver').lower()
wa = lib.getconfig.getparam('WebServer', 'webaddress').split(":")
allowed = lib.getconfig.getparam('WebServer', 'allowedip').split(",")

auth = False
try:
    key = lib.getconfig.getparam('WebServer', 'apikey')
    auth = True
except:
    auth = False


prev_value = {"prometheus": None}
def promvalue(mytype):
    try:
        if lib.pushdata.promq.qsize() != 0:
            prev_value.update({mytype: lib.pushdata.promq.get()})
            return prev_value[mytype]
        else:
            return prev_value[mytype]
    except Exception as e:
        lib.puylogger.print_message(__name__, str(e))
        pass


class SecureHTTPServer(HTTPServer):
    def get_request(self):
        sock, addr = super().get_request()
        client_ip, _ = addr
        if client_ip not in  allowed:
            lib.puylogger.print_message(f"Dropping unauthorized connection from {client_ip}")
            sock.close()
        sock.settimeout(2.0)
        return sock, addr


class PuyPuyWeb(BaseHTTPRequestHandler):
    def the_job(self):
        if self.path == '/nag':
            try:
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                ret = lib.nag.run_nag(post_body)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str.encode(ret + "\n"))
            except Exception as error:
                lib.puylogger.print_message("Something's gone werong: {}".format(error), ":Check your data please")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes("Not Found\n", "utf-8"))

    def do_GET(self):
        # self.check_client()
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            # self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            self.wfile.write(bytes(promvalue("prometheus") + "\n", "utf-8"))
        elif self.path == '/nag':
            self.send_response(501)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes("GET method is not implemented!\n", "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes("Not Found\n", "utf-8"))

    def do_POST(self):
        # self.check_client()
        if auth:
            apikey = self.headers.get('Apikey')
            if apikey == None or apikey != key:
                self.send_response(403)
                self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
                self.end_headers()
                self.wfile.write(bytes("Unauthorized\n", "utf-8"))
                # lib.puylogger.print_message(apikey)
            else:
                self.the_job()
        else:
            self.the_job()

def run_web():
    webServer = SecureHTTPServer((wa[0], int(wa[1])), PuyPuyWeb)
    lib.puylogger.print_message("Server started http://%s:%s" % (wa[0], wa[1]))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
# ------------------------------------------- #
