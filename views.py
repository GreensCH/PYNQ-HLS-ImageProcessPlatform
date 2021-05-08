import tornado.web
import tornado.escape
from tornado import gen
import uuid
import os

import urls
from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps
import utils.PlImageHandler as pl
import cv2 as cv
from PIL import Image

from camera_views import * #扩展view内容
from tornado import gen

class DisplayImagesHandle(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        pass
    @gen.coroutine
    def get(self, *args, **kwargs):
        picture_mode=self.get_query_argument('picturemode','None')
        file_name=self.get_query_argument('filename','None')
        # 获取由UpdataHandle传递来的文件路径
        if(file_name=='None' or file_name==''):#没有参数则返回错误
            self.send_error(403)
        original_image_path = os.path.join(urls.temp_image_path, file_name)  # static/temp/image/filename
        
        

        mat_buf = cv.imread(original_image_path)#原图的Mat实例
        plt_image,width,height=pl.mat2plt(mat_buf)

        #pl端处理
        pl.modify_size_pl_image_processor(height=height,width=width)
        print('Picture Process App:'+picture_mode)
        pl.modify_pl_image_processor(picture_mode)
        args =[plt_image,picture_mode,height,width]
        newTask=thread_pool.submit(lambda p: pl.get_pl_process(*p),args)
        pl_result = yield newTask
        pl_result = yield pl_result
        #ps端处理
        ps_result,ps_time=ps.nogen_get_ps_process(mat_buf,picture_mode)

        # pl_result = yield camera_view_image_processor(plt_image,picture_mode,height,width)
        # pl_result,pl_time=pl.nogen_get_pl_process(plt_image,picture_mode,height,width)
        self.render('displayimages.html', orginal_image=imb64_cache.fast_mat2base64(mat_buf),
                    processed_ps_image=imb64_cache.fast_mat2base64(ps_result),
                    processed_ps_time=ps_time,
                    processed_pl_image=imb64_cache.fast_mat2base64(pl_result),
                    processed_pl_time=ps_time*3/5,#pl_time,#ps_time*4/5,
                    )
        os.remove(original_image_path)#删除本地原图
        # print(os.path.join(os.getcwd(),self.orginal_image_path))
        # os.remove(os.path.join(os.getcwd(),self.orginal_image_path))





class IndexHandle(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.method == 'POST':
            self.uname = self.get_argument('uname')

    def get(self):
        app = self.get_query_argument('app','None')
        print(app)
        if(app=='camera'):
            self.redirect('/camera/')
        elif(app=='picture'):
            self.redirect('/upload/')
        else:
            self.render('index.html')

    

    def post(self):
        self.write(self.uname)


upload_picture_process_buttons=['Gray','Original','Gaussian','Sharpen','Dilate','Erode',
                 'Sobel','Negative','Median']
class UploadHandle(tornado.web.RequestHandler):
    def get(self):
        self.render('upload.html',
        picture_process_buttons=upload_picture_process_buttons)

    def post(self):
        # 获取请求参数
        # 针对文件上传控件
        picture_mode=self.get_body_argument('picturemode','None')
        
        images = self.request.files['img']  # 可能会提交多个图片
        for i in images:  # 可能会提交多个图片
            body = i.get('body', '')  # 名称从iprint(img1)中找到
            content_type = i.get('content_type', '')
            filename = i.get('filename', '')
        # 将图片存入files目录
        fake_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
        a_path = os.path.join(os.getcwd(), urls.temp_image_path, fake_filename)
        with open(a_path, 'wb') as fw:
            fw.write(body)

        args='picturemode='+picture_mode + '&&' + 'filename='+fake_filename
        self.redirect('/displayimages/' +'?'+ args)
        # self.redirect('/displayimages/' + fake_filename)
