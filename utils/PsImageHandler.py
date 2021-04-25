import uuid
import os
import time
import cv2 as cv
import numpy as np  # 用于mat读取
from tornado import gen
from tornado.concurrent import Future


ps_methods =['Gray','Original','Gaussian','Sharpen',
                 'Sobel','Canny']
                #{'Gray':'get_gray_matimage'}# {'Original':'get_matimage','Gray':'get_gray_matimage',
                  # 'Gaussian':'get_gaussian_blur_matimage','Sobel':'get_sobel_filter',
                  # 'Canny':'get_canny'}

#ps端图像处理对象,调用opencv库,默认内部mat
@gen.coroutine
def get_gray_matimage(mat_img):
    future = Future()
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    future.set_result(gray)
    return future

@gen.coroutine
def get_gaussian_blur_matimage(mat_img):
    future = Future()
    gaussian = cv.GaussianBlur(mat_img, (9,9), 0)
    future.set_result(gaussian)
    return future



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
@gen.coroutine
def get_sobel_filter(mat_img):
    future = Future()
    gray = cv.cvtColor(mat_img, cv.COLOR_BGR2GRAY)
    sobel_x = cv.filter2D(mat_img, -1, sobel_kernal_x)  # ddepth=-1表示相同深度
    sobel_y = cv.filter2D(mat_img, -1, sobel_kernal_y)  # ddepth=-1表示相同深度
    future.set_result(sobel_y+sobel_x)
    return future

@gen.coroutine
def get_canny(mat_img):
    future = Future()
    _canny = cv.Canny(mat_img, 50,80)
    future.set_result(_canny)
    return future


@gen.coroutine
def get_ps_process(mat_img , mode):
    if mode == ps_methods[0]:#gray
        processed_future = yield get_gray_matimage(mat_img)
    elif mode == ps_methods[1]:#original
        processed_future = Future()
        processed_future.set_result(mat_img)
    elif mode == ps_methods[2]:#Gaussian
        processed_future = yield get_gaussian_blur_matimage(mat_img)
    elif mode == ps_methods[3]:#Sobel
        processed_future = yield get_sobel_filter(mat_img)
    elif mode == ps_methods[4]:#Canny
        processed_future = yield get_canny(mat_img)
    else:
        processed_future = yield get_gray_matimage(mat_img)
    return processed_future



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
        gray = cv.cvtColor(self.mat_img, cv.COLOR_BGR2GRAY)
        sobel_x = cv.filter2D(gray, -1, self.sobel_kernal_x)  # ddepth=-1表示相同深度
        sobel_y = cv.filter2D(gray, -1, self.sobel_kernal_y)  # ddepth=-1表示相同深度
        return sobel_y+sobel_x

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