from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from queue import Queue

addr = "127.0.0.1"
port = 8037

viewQueue = Queue()


class CADViewerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers["Content-Length"])
        print("Content-Length:", len)
        data = self.rfile.read(len)
        self.send_response(200)
        self.end_headers()
        try:
            self.wfile.write(bytes("got it", "utf-8"))
        except:
            print("Exception writing response")
            pass
        viewQueue.put(data)


def start_server():
    Thread(target=_start_server, daemon=True).start()


def _start_server():
    print("Viewer server started on (", addr, port, ")")
    httpd = ThreadingHTTPServer((addr, port), CADViewerHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    start_server()
    print("^C to exit.")
    while True:
        try:
            input("")
        except KeyboardInterrupt:
            break
