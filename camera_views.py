import tornado.web
import tornado.escape
import tornado.websocket
from tornado import gen
import uuid
import os
import time
import threading

import urls
from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps
import utils.PlImageHandler as pl
import cv2 as cv

from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.gen import Return

thread_pool = None#ThreadPoolExecutor(4)
thread_pool=ThreadPoolExecutor(4)
print("thread init success")
CameraButton = ['Release IP','Reload IP']#'PS','PL','VDMA-STOP','Gray','Original','Gaussian','Sobel','Canny']


class CameraHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        self.render('camera.html',
        ws_url_home = urls.ws_url_home,
        buttons=CameraButton,
        ps_buttons=ps.ps_methods,
        pl_buttons=pl.pl_methods,
        )#渲染按键

# class VideoBackgroundHandle(tornado.websocket.WebSocketHandler):
#     def open(self, *args, **kwargs):
#        print('connected')
#        self.image64=''
#        self.out_image64=''
#        self.video_model=ps.ps_methods[0]#Refence to ps.ps_method
#        self.ps_pl='PS'#PS,PL
#        self.time_threshold = 500 #动态负载阈值
#        self.delay_time=50 #动态负载延迟
@gen.coroutine
def camera_view_image_processor(img,sz_mode,height,width):
    pl.modify_size_pl_image_processor(height=height,width=width)
    print(pl.get_pl_mode())
    pl.modify_pl_image_processor(sz_mode)
    args =[img,sz_mode,height,width]
    newTask=thread_pool.submit(lambda p: pl.get_pl_process(*p),args)
    result = yield newTask
    result = yield result
    return result;


class CameraBackgroundHandle(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
       print('connected')
       self.image64=''
       self.out_image64=''
       self.video_model=ps.ps_methods[0]#Refence to ps.ps_method
       self.ps_pl='PS'#PS,PL
       self.time_threshold = 500 #动态负载阈值
       self.delay_time=50 #动态负载延迟
       print(pl.ip_active())
       global thread_pool
       if thread_pool == None:
           thread_pool=ThreadPoolExecutor(4)
           print("thread init success")



    #接收消息时的反应
    @gen.coroutine
    def on_message(self, message):
        data = tornado.escape.json_decode(message)
        for s in data.keys():
            if s == 'VideoModel':
                if data[s] == 'Release IP':#释放button
                    print("Release IP OK")
                    pl.release_ip_mode()
                elif data[s] == 'Reload IP':
                    print("Reload IP OK")
                    pl.init_ip()
                self.ps_pl=data[s][:2]
                self.video_model=data[s][3:]
                if(self.ps_pl=='PL'):
                    pl.modify_pl_image_processor(self.video_model)
            elif s == 'ImgData':#处理图像
                self.image64 = data[s]#缓存原图
                # 实例化base64cache用于解析输入base64与缓存数据
                imb64 = imb64_cache.ImageBase64Cache(base64_str=data[s])
                if(self.ps_pl=='PL'):
                    plt_image,width,height=pl.mat2plt(imb64.mat_img)
                    if(height!=pl.get_pl_height() or width!=pl.get_pl_width()):#如果宽度不对应
                        pl.modify_size_pl_image_processor(height=height,width=width)
                    if(pl.pl_methods_dict[self.video_model] !=pl.get_pl_mode()):
                        print(pl.get_pl_mode())
                        pl.modify_pl_image_processor(self.video_model)
                    args =[plt_image,self.video_model,height,width]
                    newTask=thread_pool.submit(lambda p: pl.get_pl_process(*p),args)
                    result = yield newTask
                    result = yield result
                    self.write_message(tornado.escape.json_encode({
                        'ImgData':imb64_cache.fast_mat2base64(result),
                        'TimeDelay':self.delay_time,
                        'TimeThreshold':self.time_threshold,
                    }))
                else:
                    # 实例化PS处理器用于图像处理
                    # yield thread_pool.submit(ps.get_ps_process, imb64.mat_img)
                    args =[imb64.mat_img,self.video_model]
                    newTask=thread_pool.submit(lambda p: ps.get_ps_process(*p),args)
                    #result = thread_pool.submit(ps.get_ps_process, {'mat_img':imb64.mat_img,'mode':self.video_model})#([imb64.mat_img,self.video_model])
                    result = yield newTask
                    result = yield result
                    self.write_message(tornado.escape.json_encode({
                        'ImgData':imb64_cache.fast_mat2base64(result),
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
