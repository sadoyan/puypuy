import lib.getconfig
from http.server import BaseHTTPRequestHandler, HTTPServer
import lib.getconfig
import lib.nag
import lib.puylogger
import lib.pushdata

ws = lib.getconfig.getparam('WebServer', 'webserver').lower()
wa = lib.getconfig.getparam('WebServer', 'webaddress').split(":")

auth = False
try:
    key = lib.getconfig.getparam('WebServer', 'apikey')
    auth = True
except:
    auth = False

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
                lib.puylogger.print_message(ret)
            except Exception as error:
                lib.puylogger.print_message("Something's gone werong: {}".format(error), ":Check your data please")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes("Not Found\n", "utf-8"))

    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            # self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            data = lib.pushdata.promq.get()
            self.wfile.write(bytes(data + "\n", "utf-8"))
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
    webServer = HTTPServer((wa[0], int(wa[1])), PuyPuyWeb)
    lib.puylogger.print_message("Server started http://%s:%s" % (wa[0], wa[1]))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
# ------------------------------------------- #
