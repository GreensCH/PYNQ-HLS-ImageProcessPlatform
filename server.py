#%%
import tornado.web
import tornado.ioloop
from tornado import httpserver
from urls import settings
import os

def killport(port):
    command='''kill -9 $(netstat -nlp | grep :'''+str(port)+''' | awk '{print $7}' | awk -F"/" '{ print $1 }')'''
    os.system(command) 


app =tornado.web.Application(
    **settings
)

server = httpserver.HTTPServer(app, ssl_options={
        "certfile": os.path.join(os.path.abspath("."), "static/ssl/server.crt"),
        "keyfile": os.path.join(os.path.abspath("."), "static/ssl/server.key.unsecure"),
})

# killport(8080)
server.listen(8080)
tornado.ioloop.IOLoop.instance().start()



# %%
