import tornado.web
import tornado.escape
import tornado.websocket
from tornado import gen
import uuid
import os
import time

import urls
from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps
import utils.PlImageHandler as pl
import cv2 as cv

CameraButton = ['PS','PL','Gray','Original','Gaussian',
                 'Sobel','Canny']

class CameraHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        self.render('camera.html',
        ws_url_home = urls.ws_url_home,
        buttons=CameraButton)#渲染按键

class CameraBackgroundHandle(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
       print('connected')
       self.image64=''
       self.out_image64=''
       self.video_model=ps.ps_methods[0]#Refence to ps.ps_method
       self.ps_pl='PS'#PS,PL
       self.time_threshold = 500 #动态负载阈值
       self.delay_time=50 #动态负载延迟

    #接收消息时的反应
    @gen.coroutine
    def on_message(self, message):
        data = tornado.escape.json_decode(message)
        for s in data.keys():
            if s == 'VideoModel':
                if(data[s]=="PS"):
                    self.ps_pl=data[s]
                    # pl.resetbitstream()
                elif(data[s]=="PL"):
                    self.ps_pl=data[s]
                    # pl.loadbitstream()
                else:
                    self.video_model=data[s]
            elif s == 'ImgData':#处理图像
                self.image64 = data[s]#缓存原图
                # 实例化base64cache用于解析输入base64与缓存数据
                imb64 = imb64_cache.ImageBase64Cache(base64_str=data[s])
                if(self.ps_pl=='PL'):
                    plt_image,height,width=pl.mat2plt(imb64.mat_img)
                    processed_future= pl.get_pl_process(plt_image,self.video_model,height,width)
                    self.write_message(tornado.escape.json_encode({
                        'ImgData':imb64_cache.fast_mat2base64(processed_future),
                        'TimeDelay':self.delay_time,
                        'TimeThreshold':self.time_threshold,
                    }))
                else:
                    # 实例化PS处理器用于图像处理
                    processed_future = yield ps.get_ps_process(imb64.mat_img,self.video_model)
                    self.write_message(tornado.escape.json_encode({
                        'ImgData':imb64_cache.fast_mat2base64(processed_future._result),
                        'TimeDelay':self.delay_time,
                        'TimeThreshold':self.time_threshold,
                    }))
            elif s == 'Timeout':
                #动态调整负载
                print(data[s])#当前负载
                pass
            else:
                pass

    def on_close(self):
        print('disconnected')
    
    #允许跨域
    def check_origin(self, origin):
        return True
    
    #ping通客户端周期性要求传输图像数据，传输结束后进行协程处理后发送
    # def on_pong(self, data):
    #     # message={
    #     #     'ImgData':self.out_image64,
    #     #     'ServerTime':str(time.time())
    #     # }
    #     # json_message = tornado.escape.json_encode(message)
    #     pass
