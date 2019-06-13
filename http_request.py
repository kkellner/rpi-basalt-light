# Fountain project
#
# http_request.py - handle http requests
#

import logging
import time
from datetime import datetime
import http.server
import socketserver
import threading
import socket
from queue import Queue
import socketserver
import json
import psutil
from functools import partial
import subprocess

logger = logging.getLogger('http_request')


class HttpServer():

    PORT = 80

    def __init__(self, _fountain):

        endpointsGET = { 
            "/": "status",
            "/favicon.ico": "favicon",
            "/v1/data": "v1_data",
            "/test": "test",
            "/log": "log",
            }

        socketserver.TCPServer.allow_reuse_address = True

        handler = partial(GetRequestHandler, _fountain, endpointsGET)

        #self.httpd = socketserver.TCPServer(('0.0.0.0', PORT), handler)
        self.httpd = ThreadedHTTPServer(('0.0.0.0', HttpServer.PORT), handler)

    def run(self):
        logger.info("serving at port: %d", HttpServer.PORT)
        #self.httpd.serve_forever(poll_interval=5)
        self.httpd.serve_forever()
        logger.info("after serve_forever")

    def shutdown(self):
        self.httpd.server_close()
        self.httpd._BaseServer__shutdown_request = True
        # httpd.shutdown()



# Docs: https://docs.python.org/3/library/http.server.html


class GetRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Class for handling a request to the root path /
    """

    def __init__(self, basalt, endpointsGET, *args, **kwargs):
        # NOTE: A new instance of this class is created for EVERY request
        #logger.info("init GetRequestHandler")
        self.basalt = basalt
        self.endpointsGET = endpointsGET
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        logger.debug(format % args)

    def do_GET(self):
        pathOnly = self.path.split('?')[0]
        methodSuffix = self.endpointsGET.get(pathOnly, None)
        if methodSuffix is not None:
            handlerMethodName = "get_" + methodSuffix
            handlerMethod = getattr(self, handlerMethodName)
            result = handlerMethod()
            return result
        else:
            self.send_response(404)
            self.addCORSHeaders()
            self.end_headers()            

    def do_POST(self):
        print('-----------------------')
        print('POST %s (from client %s)' % (self.path, self.client_address))
        print(self.headers)
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        print(json.dumps(post_data, indent=4, sort_keys=True))
        self.send_response(200)
        self.end_headers()

    def get_status(self):
        # serve the file!
        self.path = "status.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def get_favicon(self):
        # serve the file!
        self.path = "images/favicon.ico"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def get_log(self):
        cmd = "cat /var/log/basalt_data.log.1 /var/log/basalt_data.log  2>/dev/null  | tail -n 40"
        self.run_command(cmd)
        
    def run_command(self, cmd):

        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        cmdOutput = p.stdout.strip()


        # Write the response
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200, 'OK')
        self.send_header('Connection', 'Keep-Alive')
        self.addCORSHeaders()

        self.send_header('Content-type', 'text/plain;charset=UTF-8')
        self.send_header("Content-Length", str(len(cmdOutput)))
        self.end_headers()
        self.wfile.write(bytes(cmdOutput, 'utf-8'))


    def get_v1_data(self):
        

        rpiInfo = self.fountain.rpi_info.get_info()

        response = {
                "cpuPercent": psutil.cpu_percent(),
                "rpiTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "rpiInfo": rpiInfo
            }

        data = json.dumps(response)

        # Write the response
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200, 'OK')
        self.send_header('Connection', 'Keep-Alive')
        self.addCORSHeaders()

        self.send_header('Content-type', 'application/json')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(bytes(data, 'utf-8'))
        return

    def addCORSHeaders(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                            'GET,PUT,POST,DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('X-Content-Type-Options', 'nosniff')

# Source of below code: http://code.activestate.com/recipes/574454-thread-pool-mixin-class-for-use-with-socketservert/
class ThreadPoolMixIn(socketserver.ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    numThreads = 10
    allow_reuse_address = True  # seems to fix socket.error on server restart

    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        # set up the threadpool
        self.requests = Queue(self.numThreads)

        for x in range(self.numThreads):
            t = threading.Thread(target=self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while True:
            self.handle_request()

        self.server_close()

    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        # The thread starts and stays on this loop.
        # The method call hangs waiting until something is inserted into self.requests
        #  and .get() unblocks
        while True:
            socketserver.ThreadingMixIn.process_request_thread(self, *self.requests.get())

    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))


class ThreadedHTTPServer(ThreadPoolMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""
    pass