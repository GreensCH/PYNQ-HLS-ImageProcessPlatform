from views import *
import os

url_home = 'https://192.168.0.100:8080'
ws_url_home = 'ws://192.168.0.100:8080'

temp_image_path = os.path.join('static', 'temp', 'images')  # static/temp/image
camera_methods = {'Original':'get_matimage','Gray':'get_gray_matimage',
                  'Gaussian':'get_gaussian_blur_matimage','Sobel':'get_sobel_filter',
                  'Canny':'get_canny'}

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
    'websocket_ping_interval' : camera_ws_ping_interval,
}
