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
    def _handle_header(directory_route):

        header = 'HTTP/1.1 200 OK\n'

        if os.path.isfile(directory_route):
            mime_type = mimetypes.guess_type(directory_route)[0]

            if mime_type:
                header += 'Content-Type: %s\n' % mime_type
            else:
                header += 'Content-Type: text/plain\n'

        else:
            header += 'Content-Type: text/html\n'

        header += 'Connection: keep-alive\n\n'

        header = header.encode()

        return header

    @staticmethod
    def _handle_body(directory_route, request_route):

        if os.path.isfile(directory_route):
            with open(directory_route, 'rb') as inf:
                body = inf.read()

        else:
            directories = os.listdir(directory_route)

            if 'index.html' in directories:
                logger.info('Found an index, on route %s.', directory_route)
                index_route = directory_route + '/index.html'
                with open(index_route, 'rb') as inf:
                    body = inf.read()

            else:
                logger.info('Returning directory list on route %s.', request_route)

                body_hat = '<html>\n<head>\n<title>Contents</title>\n<span >Directory listing for %s</span>\n<hr>\n \
                </head>\n<body>\n<ul>' % request_route

                body_center = ""

                for item in directories:
                    body_center += "<li><a href='%s%s" % (request_route, item)
                    if os.path.isdir("%s/%s" % (directory_route, item)):
                        body_center += "/"
                    body_center += "'>%s</a></li>\n" % item

                body_bottom = '</ul>\n<hr>\n</body>\n</html>'

                body = (body_hat + body_center + body_bottom).encode()

        return body

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

            header = self._handle_header(directory_route)

            body = self._handle_body(directory_route, request_route)

            response = header + body

            conn.send(response)

        finally:
            conn.close()

    def run(self):

        logger.info('Starting event loop.')
        while True:
            self._handle_request()
