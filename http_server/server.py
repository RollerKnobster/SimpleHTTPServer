import socket
import os
import mimetypes
import logging
from .logger import logger

logger.setLevel(logging.DEBUG)


class HttpServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            logger.info('Initializing server on %s:%d' % (self.host, self.port))
            self.socket.bind((self.host, self.port))
            logger.info('Connected to port %d' % self.port)

        except OSError:

            try:
                logger.info('Trying to connect to port %d' % (self.port+1))
                self.socket.bind((self.host, self.port+1))
                logger.info('Connected to port %d' % (self.port + 1))

            except OSError:
                logger.info('Server Shutdown')
                self.socket.shutdown(socket.SHUT_RDWR)

    @staticmethod
    def _handle_response(route, item_route):
        header = 'HTTP/1.1 200 OK\n'

        header += 'Content-Type: text/html\n'

        directories = os.listdir(route)

        if 'index.html' in directories:
            logger.info('Found an index, on route %s.', route)
            index_route = route + '/index.html'
            with open(index_route, 'rb') as inf:
                body = bytes.decode(inf.read())

        else:
            logger.info('Returning directory list on route %s.', item_route)

            body_hat = '<html>\n<head>\n<title>Contents</title>\n<span >Directory listing for %s</span>\n<hr>\n \
            </head>\n<body>\n<ul>' % item_route

            body_center = ""

            for item in directories:
                body_center += "<li><a href='%s%s" % (item_route, item)
                if os.path.isdir("%s/%s" % (route, item)):
                    body_center += "/"
                body_center += "'>%s</a></li>\n" % item

            body_bottom = '</ul>\n<hr>\n</body>\n</html>'

            body = body_hat + body_center + body_bottom

        header += 'Connection: keep-alive\n\n'

        logger.info('Header itself: \n %s' % header)

        res = header + body

        return res

    def _handle_request(self):
        self.socket.listen(10)
        conn, addr = self.socket.accept()

        try:
            data = conn.recv(1024)
            request_string = bytes.decode(data)

            logger.info('Request string: \n %s' % request_string)

            request_route = request_string.split(' ')[1].replace("%20", " ")

            logger.info('Handling request on route %s' % request_route)

            directory_route = os.getcwd() + request_route

            if os.path.isfile(directory_route):
                logger.info('Sending a file, route %s', directory_route)

                header = 'HTTP/1.1 200 OK\n'

                mime_type = mimetypes.guess_type(directory_route)[0]

                if mime_type:
                    header += 'Content-Type: %s\n' % mime_type
                else:
                    header += 'Content-Type: text/plain\n'

                header += 'Connection: keep-alive\n\n'

                conn.sendall(header.encode())

                with open(directory_route, 'rb') as inf:
                    conn.sendfile(inf)

            else:
                response = self._handle_response(directory_route, request_route).encode()

                conn.send(response)

        finally:
            conn.close()

    def run(self):
        logger.info('Starting event loop.')
        while True:
            self._handle_request()
