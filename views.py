import tornado.web
import tornado.escape
from tornado import gen
import uuid
import os

import urls
from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps
import cv2 as cv

from camera_views import * #扩展view内容


class DisplayImagesHandle(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        pass
    def get(self, filename, *args, **kwargs):
        # 获取由UpdataHandle传递来的文件路径
        original_image_path = os.path.join(urls.temp_image_path, filename)  # static/temp/image/filename
        
        mat_buf = cv.imread(original_image_path)#原图的Mat实例
        my_ps = ps.PsImageHandler(mat_buf)#传入图片，并实例一个PsImageHandler
        gray_img,time = my_ps.get_gray_matimage()#调用实例方法，返回图片

        self.render('displayimages.html', orginal_image=imb64_cache.fast_mat2base64(mat_buf),
                    processed_ps_image=imb64_cache.fast_mat2base64(gray_img),
                    processed_ps_time=time,
                    processed_pl_image=imb64_cache.fast_mat2base64(gray_img),
                    processed_pl_time=0,
                    )
        os.remove(original_image_path)
        # print(os.path.join(os.getcwd(),self.orginal_image_path))
        # os.remove(os.path.join(os.getcwd(),self.orginal_image_path))





class IndexHandle(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.method == 'POST':
            self.uname = self.get_argument('uname')

    def get(self):
        self.render('index.html')

    def post(self):
        self.write(self.uname)


class UploadHandle(tornado.web.RequestHandler):
    def get(self):
        self.render('upload.html')

    def post(self):
        # 获取请求参数
        # 针对文件上传控件
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
        self.redirect('/displayimages/' + fake_filename)
