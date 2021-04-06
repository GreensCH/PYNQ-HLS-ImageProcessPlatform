import tornado.web
import tornado.ioloop
from tornado import httpserver
from urls import settings
import os


app =tornado.web.Application(
    **settings
)

server = httpserver.HTTPServer(app, ssl_options={
        "certfile": os.path.join(os.path.abspath("."), "static/ssl/server.crt"),
        "keyfile": os.path.join(os.path.abspath("."), "static/ssl/server.key.unsecure"),
})

server.listen(8080)
tornado.ioloop.IOLoop.instance().start()


