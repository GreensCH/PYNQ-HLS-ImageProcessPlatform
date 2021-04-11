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
import cv2 as cv


class CameraHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        self.render('camera.html',
        ws_url_home = urls.ws_url_home,
        buttons=urls.camera_methods)#渲染按键

class CameraBackgroundHandle(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
       print('connected')
       self.image64=''
       self.out_image64=''
       self.video_model=list(urls.camera_methods.keys())[0]#Refence to urls.camera_methods
       self.ps_pl='PS'#PS,PL
       self.time_threshold = 300 #动态负载阈值
       self.delay_time=200 #动态负载延迟

    #接收消息时的反应
    def on_message(self, message):
        data = tornado.escape.json_decode(message)
        for s in data.keys():
            if s == 'VideoModel':
                self.video_model=data[s]
            elif s == 'ImgData':#处理图像
                self.image64 = data[s]#缓存原图
                # 实例化base64cache用于解析输入base64与缓存数据
                imb64 = imb64_cache.ImageBase64Cache(base64_str=data[s])
                if(self.ps_pl=='PL'):
                    pass
                else:
                    # 实例化PS处理器用于图像处理
                    my_ps = ps.PsImageHandler(imb64.mat_img)
                    ps_func = getattr(my_ps, urls.camera_methods[self.video_model])  #匹配方法 可以人工改成switch，提高速度
                    processed_mat, time = ps_func()
                    self.write_message(tornado.escape.json_encode({
                        'ImgData':imb64_cache.fast_mat2base64(processed_mat),
                        'TimeDelay':self.delay_time,
                        'TimeThreshold':self.time_threshold,
                    }))
            elif s == 'PSPL':#PS or PL
                self.ps_pl=data[s]
            elif s == 'Timeout':
                #动态调整负载
                # print(data[s])#当前负载
                pass
            else:
                pass

    def on_close(self):
        print('disconnected')
    
    #允许跨域
    def check_origin(self, origin):
        return True
    