import tornado.web
import tornado.escape
import tornado.websocket
from tornado import gen
import uuid
import os

import urls
from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps
import cv2 as cv

fps = 30
camera_ws_ping_interval = 1/fps

class CameraHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        self.render('camera.html',
        ws_url_home = urls.ws_url_home,
        buttons=urls.camera_methods)#渲染按键

class CameraBackgroundHandle(tornado.websocket.WebSocketHandler):
   def open(self, *args, **kwargs):
       print('connected')

    #接收消息时的反应
    def on_message(self, message):
        print(message)
        data = tornado.escape.json_decode(message)
        for s in data.keys():
            if s == 'VideoModel':
                self.video_model=data[s]
            elif s == 'ImgData':
                self.image64=data[s]
            elif s == 'PSPL':#PS or PL
                self.ps_pl=data[s]

    def on_close(self):
        print('disconnected')
    
    #允许跨域
    def check_origin(self, origin):
        return True
    
    #ping通客户端周期性要求传输图像数据，传输结束后进行协程处理后发送
    def on_pong(self, data):
        print('on_pong')
        self.write_message(self.image64)


        # self.write_message(self.camera_cache)#发送上一帧处理结束图片

    # def get(self, *args, **kwarg):
    #     print('CameraBackground Get')

    # def post(self, *args, **kwargs):
    #     self.set_header('Access-Control-Allow-Origin', '*')  # 允许跨域
    #     self.set_header('Access-Control-Allow-Headers', '*')  # 允许所有请求头
    #     data = tornado.escape.json_decode(self.request.body)
    #     # 实例化base64cache用于解析输入base64与缓存数据
    #     imb64 = imb64_cache.ImageBase64Cache(base64_str=data['ImgData'])
    #     # 实例化PS处理器用于图像处理
    #     my_ps = ps.PsImageHandler(imb64.mat_img)

    #     video_model=data['VideoModel']
    #     if(video_model not in urls.camera_methods.keys()):#是否定义该方法
    #         video_model='Original'#没有该方法则归为原图
    #     elif(urls.camera_methods[video_model]==''):#是否定义该方法
    #         video_model='Original'#没有定义该方法则归为原图

    #     ps_func = getattr(my_ps,urls.camera_methods[video_model])#可以人工改成switch，提高速度
    #     processed_mat, time=ps_func()

    #     output = imb64_cache.fast_mat2base64(processed_mat)
    #     self.write(output)