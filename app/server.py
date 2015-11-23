import socket
import uuid
import tornado.escape

import tornado.iostream
import tornado.gen
import tornado.tcpserver
from client import MessageSocketHandler, SourceSocketHandler


class TcpClient(object):
    client_id = 0

    def __init__(self):
        TcpClient.client_id += 1

        self.id = TcpClient.client_id
        self.auth = False
        self.source_name = ''

        self.stream = None

    def _login(self, source_name):
        self.auth = True
        self.source_name = source_name

        SourceSocketHandler.add_source(source_name)
        SourceSocketHandler.send_updates()

    def _logout(self):
        if self.source_name:
            SourceSocketHandler.remove_source(self.source_name)
        SourceSocketHandler.send_updates()

        self.auth = False
        self.source_name = ''

    def set_stream(self, stream):
        self.stream = stream
        self.stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.set_close_callback(self.on_disconnect)

    @tornado.gen.coroutine
    def on_connect(self):
        remote_addr = 'closed'
        try:
            remote_addr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass

        self.log('new, %s' % remote_addr)
        TcpServer.clients.add(self.id)

        yield self.dispatch_client()

    @tornado.gen.coroutine
    def on_disconnect(self):
        self.log("disconnected")
        TcpServer.clients.remove(self.id)
        self._logout()
        yield []

    @tornado.gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')

                line = self.clean_line(line)
                self.log('got |%s|' % line)

                login = self.process_auth(line)

                if self.auth and not login:
                    message = self.process_line(line)
                    if message:
                        MessageSocketHandler.update_cache(message)
                        MessageSocketHandler.send_updates(message)

        except tornado.iostream.StreamClosedError:
            pass

    def log(self, msg, *args, **kwargs):
        print('[connection %d] %s' % (self.id, msg.format(*args, **kwargs)))

    def clean_line(self, line):
        return line.decode('utf-8').strip()

    def process_auth(self, line):
        login = False

        if self.auth and line == 'End':
            self._logout()
        elif not self.auth and line.startswith('Auth:: '):  # check for auth message
            self._login(line[7:])
            login = True

        return login

    def process_line(self, line):
        message = None

        kv = line.split(':: ')
        if len(kv) == 2:
            key, value = kv
            message = {
                "id": str(uuid.uuid4()),
                'source': self.source_name,
                'key': key,
                'value': value,
            }

        return message


class TcpServer(tornado.tcpserver.TCPServer):
    clients = set()

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        client = TcpClient()
        client.set_stream(stream)

        yield client.on_connect()
