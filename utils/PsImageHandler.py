import uuid
import os
import time
import cv2 as cv
import numpy as np  # 用于mat读取
from tornado import gen
from tornado.concurrent import Future
from tornado.gen import Return

ps_methods = ['Gray','Original','Gaussian','Sharpen','Dilate','Erode',
                 'Sobel','Canny','Negative','Median']
                #{'Gray':'get_gray_matimage'}# {'Original':'get_matimage','Gray':'get_gray_matimage',
                  # 'Gaussian':'get_gaussian_blur_matimage','Sobel':'get_sobel_filter',
                  # 'Canny':'get_canny'}




sobel_kernal_x=np.array([
    [-1,0,1],
    [-2,0,2],
    [-1,0,1]
])
sobel_kernal_y=np.array([
    [-1,-2,-1],
    [0,0,0],
    [1,2,1]
])
laplace_kernal=np.array([
    [0,-1,0],
    [-1,5,-1],
    [0,-1,0]
])
#ps端图像处理对象,调用opencv库,默认内部mat
@gen.coroutine
def get_gray_matimage(mat_img):
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    raise Return(gray)

@gen.coroutine
def get_gaussian_blur_matimage(mat_img):
    gaussian = cv.GaussianBlur(mat_img, (9,9), 0)
    raise Return(gaussian)
@gen.coroutine
def get_sobel_filter(mat_img):
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    sobel_x = cv.filter2D(mat_img, -1, sobel_kernal_x)  # ddepth=-1表示相同深度
    sobel_y = cv.filter2D(mat_img, -1, sobel_kernal_y)  # ddepth=-1表示相同深度
    raise Return(sobel_y+sobel_x)
@gen.coroutine
def get_sharpen_filter(mat_img):
    # gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    _sharpen = cv.filter2D(mat_img, -1, laplace_kernal)  # ddepth=-1表示相同深度
    raise Return(_sharpen)

@gen.coroutine
def get_canny(mat_img):
    _canny = cv.Canny(mat_img, 50,80)
    raise Return(_canny)

@gen.coroutine
def get_erode(mat_img):
    _erosion = cv.erode(mat_img,np.ones((5,5),np.uint8),iterations = 1)
    raise Return(_erosion)

@gen.coroutine
def get_dilate(mat_img):
    _dilate = cv.dilate(mat_img,np.ones((5,5),np.uint8),iterations = 1)
    raise Return(_dilate)

@gen.coroutine
def get_median(mat_img):
    _median = cv.medianBlur(mat_img,5)
    raise Return(_median)

@gen.coroutine
def get_negative(mat_img):
    b,g,r=cv.split(mat_img)
    b2=255-b
    g2=255-g
    r2=255-r
    raise Return([b2,g2,r2])
    # raise Return(mat_img)

@gen.coroutine
def get_original(mat_img):
    raise Return(mat_img)

@gen.coroutine
def get_ps_process(mat_img , mode):
    time.sleep(0.05)
    if mode == 'Gray':#gray
        processed_future = yield get_gray_matimage(mat_img)
    elif mode == 'Original':#original
        processed_future = yield get_original(mat_img)
    elif mode == 'Gaussian':#Gaussian
        processed_future = yield get_gaussian_blur_matimage(mat_img)
    elif mode == 'Sharpen':
        processed_future = yield get_sharpen_filter(mat_img)
    elif mode == 'Sobel':#Sobel
        processed_future = yield get_sobel_filter(mat_img)
    elif mode == 'Canny':
        processed_future = yield get_canny(mat_img)
    elif mode == 'Dilate':
        processed_future = yield get_dilate(mat_img)
    elif mode == 'Erode':
        processed_future = yield get_erode(mat_img)
    elif mode == 'Negative':
        processed_future = yield get_negative(mat_img)
    elif mode == 'Median':
        processed_future = yield get_median(mat_img)
    else:
        processed_future = yield get_gray_matimage(mat_img)
    return processed_future




#ps端图像处理对象,调用opencv库,默认内部mat
def nogen_get_gray_matimage(mat_img):
    _time_start=time.time()
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    return gray,time.time()-_time_start

def nogen_get_gaussian_blur_matimage(mat_img):
    _time_start=time.time()
    gaussian = cv.GaussianBlur(mat_img, (9,9), 0)
    return gaussian,time.time()-_time_start

def nogen_get_sobel_filter(mat_img):
    _time_start=time.time()
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    sobel_x = cv.filter2D(mat_img, -1, sobel_kernal_x)  # ddepth=-1表示相同深度
    sobel_y = cv.filter2D(mat_img, -1, sobel_kernal_y)  # ddepth=-1表示相同深度
    return sobel_y+sobel_x,time.time()-_time_start

def nogen_get_sharpen_filter(mat_img):
    _time_start=time.time()
    # gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    _sharpen = cv.filter2D(mat_img, -1, laplace_kernal)  # ddepth=-1表示相同深度
    return _sharpen,time.time()-_time_start

def nogen_get_canny(mat_img):
    _time_start=time.time()
    _canny = cv.Canny(mat_img, 50,80)
    return _canny,time.time()-_time_start

def nogen_get_erode(mat_img):
    _time_start=time.time()
    _erosion = cv.erode(mat_img,np.ones((5,5),np.uint8),iterations = 1)
    return _erosion,time.time()-_time_start

def nogen_get_dilate(mat_img):
    _time_start=time.time()
    _dilate = cv.dilate(mat_img,np.ones((5,5),np.uint8),iterations = 1)
    return _dilate,time.time()-_time_start

def nogen_get_median(mat_img):
    _time_start=time.time()
    _median = cv.medianBlur(mat_img,5)
    return _median,time.time()-_time_start

def nogen_get_negative(mat_img):
    _time_start=time.time()
    b,g,r=cv.split(mat_img)
    b=255-b
    g=255-g
    r=255-r
    mat_img[:,:,0]=b
    mat_img[:,:,1]=g
    mat_img[:,:,2]=r
    return mat_img,time.time()-_time_start

def nogen_get_ps_process(mat_img , mode):
    # time.sleep(0.05)
    process_time=-1;
    if mode == 'Gray':#gray
        processed_image,process_time = nogen_get_gray_matimage(mat_img)
    elif mode == 'Original':#original
        processed_image = mat_img
    elif mode == 'Gaussian':#Gaussian
        processed_image,process_time = nogen_get_gaussian_blur_matimage(mat_img)
    elif mode == 'Sharpen':
        processed_image,process_time = nogen_get_sharpen_filter(mat_img)
    elif mode == 'Sobel':#Sobel
        processed_image,process_time = nogen_get_sobel_filter(mat_img)
    elif mode == 'Canny':
        processed_image,process_time = nogen_get_canny(mat_img)
    elif mode == 'Dilate':
        processed_image,process_time = nogen_get_dilate(mat_img)
    elif mode == 'Erode':
        processed_image,process_time = nogen_get_erode(mat_img)
    elif mode == 'Negative':
        processed_image,process_time = nogen_get_negative(mat_img)
    elif mode == 'Median':
        processed_image,process_time = nogen_get_median(mat_img)
    else:
        processed_image,process_time = nogen_get_gray_matimage(mat_img)
    return processed_image,process_time


class PsImageHandler():
    sobel_kernal_x=np.array([
        [-1,0,1],
        [-2,0,2],
        [-1,0,1]
    ])
    sobel_kernal_y=np.array([
        [-1,-2,-1],
        [0,0,0],
        [1,2,1]
    ])

    def __init__(self, mat_img,*args, **kwarg):
        self.mat_img = mat_img

    def img_show(self):
        cv.imshow('Image', self.mat_img)
        cv.waitKey(0)

    def get_matimage(self):
        return self.mat_img;

    @gen.coroutine
    def get_gray_matimage(self):
        future = Future()
        gray = cv.cvtColor(self.mat_img, cv.COLOR_BGR2GRAY)
        future.set_result(gray)
        return future

    def get_gaussian_blur_matimage(self):
        return cv.GaussianBlur(self.mat_img, (17,17), 0)

    def get_sobel_filter(self):
        t0=time.time()
        gray = cv.cvtColor(self.mat_img, cv.COLOR_BGR2GRAY)
        sobel_x = cv.filter2D(gray, -1, self.sobel_kernal_x)  # ddepth=-1表示相同深度
        sobel_y = cv.filter2D(gray, -1, self.sobel_kernal_y)  # ddepth=-1表示相同深度
        return sobel_y+sobel_x,time.time()-t0

    def get_resize(self):
        pass

    def get_canny(self):
        return cv.Canny(self.mat_img, 50,100)


# if __name__ == '__main__':
#     img_file = cv.imread('../static/1.jpg')  # 二进制打开图片文件
#     gray = cv.cvtColor(img_file, cv.COLOR_BGR2GRAY)
#     kernal_x=np.array([
#         [-1,0,1],
#         [-2,0,2],
#         [-1,0,1]
#     ])
#     kernal_y=np.array([
#         [-1,-2,-1],
#         [0,0,0],
#         [1,2,1]
#     ])
#     sobel_x=cv.filter2D(gray,-1,kernal_x)#ddepth=-1表示相同深度
#     sobel_y=cv.filter2D(gray,-1,kernal_y)#ddepth=-1表示相同深度
#     cv.namedWindow("sobelx");
#     # cv.resizeWindow('sobelx',200,200)
#     cv.imshow('sobelx',sobel_x)

#     cv.namedWindow("sobely");
#     # cv.resizeWindow('sobelx',200,200)
#     cv.imshow('sobely',sobel_y)

#     cv.namedWindow("sobel");
#     # cv.resizeWindow('sobelx',200,200)
#     cv.imshow('sobel',sobel_x+sobel_y)
#     cv.waitKey(0)