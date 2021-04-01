import tornado.web
import tornado.escape
from tornado import gen
import uuid
import os

from utils import ImageBase64Cache as imb64_cache
from utils import PsImageHandler as ps

temp_image_path = os.path.join('static', 'temp', 'images')  # static/temp/image
camera_methods = {'Original':'get_matimage','Gray':'get_gray_matimage',
                  'Gaussian':'get_gaussian_blur_matimage','Sobel':'get_sobel_filter'}

class DisplayImagesHandle(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        pass
    def get(self, filename, *args, **kwargs):
        # 获取由UpdataHandle传递来的文件路径
        orginal_image_path = os.path.join(temp_image_path, filename)  # static/temp/image/filename
        import cv2 as cv
        mat_buf = cv.imread(orginal_image_path)#原图的Mat实例
        my_ps = ps.PsImageHandler(mat_buf)#传入图片，并实例一个PsImageHandler
        gray_img,time = my_ps.get_gray_matimage()#调用实例方法，返回图片

        self.render('displayimages.html', orginal_image=imb64_cache.fast_mat2base64(mat_buf),
                    processed_ps_image=imb64_cache.fast_mat2base64(gray_img),
                    processed_ps_time=time,
                    processed_pl_image=imb64_cache.fast_mat2base64(gray_img),
                    processed_pl_time=0,
                    )
        os.remove(orginal_image_path)
        # print(os.path.join(os.getcwd(),self.orginal_image_path))
        # os.remove(os.path.join(os.getcwd(),self.orginal_image_path))


class CameraHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        self.render('camera.html',buttons=camera_methods)#渲染按键

class CameraBackgroundHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwarg):
        print('CameraBackground Get')

    def post(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', '*')  # 允许跨域
        self.set_header('Access-Control-Allow-Headers', '*')  # 允许所有请求头
        data = tornado.escape.json_decode(self.request.body)
        # 实例化base64cache用于解析输入base64与缓存数据
        imb64 = imb64_cache.ImageBase64Cache(base64_str=data['ImgData'])
        # 实例化PS处理器用于图像处理
        my_ps = ps.PsImageHandler(imb64.mat_img)

        video_model=data['VideoModel']
        if(video_model not in camera_methods.keys()):#是否定义该方法
            video_model='Original'#没有该方法则归为原图
        elif(camera_methods[video_model]==''):#是否定义该方法
            video_model='Original'#没有定义该方法则归为原图

        ps_func = getattr(my_ps,camera_methods[video_model])#可以人工改成switch，提高速度
        processed_mat, time=ps_func()

        output = imb64_cache.fast_mat2base64(processed_mat)
        self.write(output)


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
        imgs = self.request.files['img']  # 可能会提交多个图片
        for i in imgs:  # 可能会提交多个图片
            body = i.get('body', '')  # 名称从iprint(img1)中找到
            content_type = i.get('content_type', '')
            filename = i.get('filename', '')
        # 将图片存入files目录
        fake_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
        a_path = os.path.join(os.getcwd(), temp_image_path, fake_filename)
        with open(a_path, 'wb') as fw:
            fw.write(body)
        self.redirect('/displayimages/' + fake_filename)
