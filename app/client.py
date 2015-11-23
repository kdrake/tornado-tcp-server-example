import logging
import os.path
import tornado.escape
import tornado.web
import tornado.websocket


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomepageHandler),
            (r"/m-ws", MessageSocketHandler),
            (r"/s-ws", SourceSocketHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), '..', "templates"),
            static_path=os.path.join(os.path.dirname(__file__), '..', "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class HomepageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("homepage.html",
                    messages=MessageSocketHandler.messages,
                    sources=SourceSocketHandler.sources)


class SourceSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    sources = set()

    def get_compression_options(self):
        return {}

    def open(self):
        SourceSocketHandler.waiters.add(self)

    def on_close(self):
        SourceSocketHandler.waiters.remove(self)

    @classmethod
    def add_source(cls, source):
        cls.sources.add(source)

    @classmethod
    def remove_source(cls, source):
        cls.sources.remove(source)

    @classmethod
    def send_updates(cls):
        for waiter in cls.waiters:
            try:
                message = {
                    'html': tornado.escape.to_basestring(waiter.render_string("source-list.html", sources=cls.sources))}
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)


class MessageSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    messages = []
    cache_size = 200

    def get_compression_options(self):
        return {}

    def open(self):
        MessageSocketHandler.waiters.add(self)

    def on_close(self):
        MessageSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, message):
        cls.messages.append(message)
        if len(cls.messages) > cls.cache_size:
            cls.messages = cls.messages[-cls.cache_size:]

    @classmethod
    def send_updates(cls, message):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                message["html"] = tornado.escape.to_basestring(waiter.render_string("message.html", message=message))
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
