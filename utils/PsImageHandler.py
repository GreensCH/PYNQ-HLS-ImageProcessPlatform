import uuid
import os
import time
import cv2 as cv
import numpy as np  # 用于mat读取

#ps端图像处理对象,调用opencv库,默认内部mat
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
        return self.mat_img,0;

    def get_gray_matimage(self):
        process_time = time.time()
        gray = cv.cvtColor(self.mat_img, cv.COLOR_BGR2GRAY)
        process_time = time.time() - process_time
        return gray,process_time



    def get_gaussian_blur_matimage(self):
        return cv.GaussianBlur(self.mat_img, (17,17), 0),0

    def get_sobel_filter(self):
        process_time = time.time()
        gray = cv.cvtColor(self.mat_img, cv.COLOR_BGR2GRAY)
        sobel_x = cv.filter2D(gray, -1, self.sobel_kernal_x)  # ddepth=-1表示相同深度
        sobel_y = cv.filter2D(gray, -1, self.sobel_kernal_y)  # ddepth=-1表示相同深度
        return sobel_y+sobel_x,(time.time() - process_time)

    def get_resize(self):
        pass

    def get_canny(self):
        return cv.Canny(self.mat_img, 50,100),0
    # 被抛弃的方法
    # def download_gray_image(self, src_image_path):
    #     image = cv.imread(src_image_path, cv.IMREAD_UNCHANGED)
    #     gray,time = self.get_gray_matimage()
    #     outfilename = str(uuid.uuid4()) + os.path.splitext(src_image_path)[1]#保存文件名
    #     outfiledir = os.path.split(src_image_path)[0] #保存目录(不带保存文件名)
    #     out_image_path = outfiledir + os.path.sep + outfilename #保存路径
    #     cv.imwrite(out_image_path, gray)
    #     return out_image_path,time
    #

if __name__ == '__main__':
    img_file = cv.imread('../static/1.jpg')  # 二进制打开图片文件
    gray = cv.cvtColor(img_file, cv.COLOR_BGR2GRAY)
    kernal_x=np.array([
        [-1,0,1],
        [-2,0,2],
        [-1,0,1]
    ])
    kernal_y=np.array([
        [-1,-2,-1],
        [0,0,0],
        [1,2,1]
    ])
    sobel_x=cv.filter2D(gray,-1,kernal_x)#ddepth=-1表示相同深度
    sobel_y=cv.filter2D(gray,-1,kernal_y)#ddepth=-1表示相同深度
    cv.namedWindow("sobelx");
    # cv.resizeWindow('sobelx',200,200)
    cv.imshow('sobelx',sobel_x)

    cv.namedWindow("sobely");
    # cv.resizeWindow('sobelx',200,200)
    cv.imshow('sobely',sobel_y)

    cv.namedWindow("sobel");
    # cv.resizeWindow('sobelx',200,200)
    cv.imshow('sobel',sobel_x+sobel_y)
    cv.waitKey(0)