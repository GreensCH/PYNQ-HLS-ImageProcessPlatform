from views import *
import os


url_home = 'http://127.0.0.1:8080'

settings={
    'handlers':[
        (r'/index/', IndexHandle),#起始页面
        (r'/upload/', UploadHandle),#上传页面
        (r'/displayimages/(.*)', DisplayImagesHandle),
        (r'/camera/(.*)', CameraHandle),#camera演示界面
        (r'/camera-process/', CameraBackgroundHandle)#处理相应
    ],
    'template_path':os.path.join(os.getcwd(), 'templates'),
    'static_path':os.path.join(os.getcwd(), 'static'),
}
