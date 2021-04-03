import tornado.web
import tornado.ioloop
from urls import settings


class HttpServer(tornado.web.Application):
    def __init__(self, port=8080):
        self.listen(port,address="127.0.0.1")
        tornado.web.Application.__init__(self, **settings)

    def start(self):
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    HttpServer().start()

