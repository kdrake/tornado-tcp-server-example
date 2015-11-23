import tornado.ioloop
import tornado.options
from tornado.options import define, options

from app.server import TcpServer
from app.client import Application

define("app_port", default=8888, help="web app port", type=int)
define("tcp_server_port", default=8008, help="tcp server port", type=int)


def main():
    tornado.options.parse_command_line()

    # tcp server
    server = TcpServer()
    server.listen(options.tcp_server_port)
    print("TcpServer listening on localhost:%d..." % options.tcp_server_port)

    # web app
    app = Application()
    app.listen(options.app_port)
    print("Application listening on http://localhost:%d..." % options.app_port)

    # infinite loop
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
