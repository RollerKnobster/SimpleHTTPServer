import sys
from http_server import HttpServer

HOST = '0.0.0.0'

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 8000

app = HttpServer(host=HOST, port=PORT)

if __name__ == "__main__":
    app.run()
