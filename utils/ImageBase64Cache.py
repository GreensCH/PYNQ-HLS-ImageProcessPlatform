from utils import PsImageHandler
import base64  # 用于mat读取
import cv2 as cv
import numpy as np  # 用于mat读取

import uuid
import os

DEFAULT_HEADER = 'data:image/jpg;base64,'


def base642mat(base64_img):
    img_b64decode = base64.b64decode(base64_img)  # base64解码
    img_array = np.frombuffer(img_b64decode, np.uint8)  # 转换np序列
    return cv.imdecode(img_array, cv.COLOR_BGR2RGB)  # 转换Opencv格式


def fast_mat2base64(mat_img):
    image = cv.imencode('.jpg', mat_img)[1]
    return DEFAULT_HEADER + str(base64.b64encode(image))[2:-1]



# 进行数据转换和存储的ip
class ImageBase64Cache:
    #var: header , base64_bytes_img , mat_img
    def __init__(self, base64_str='', base64_bytes=b'', *args, **kwarg):
        # 对字符串类base64进行处理，包括提取data头
        if (base64_str != ''):  # 判断是否为字符串
            if 'data' in base64_str[:22]:  # 如果存在data头
                self.header = base64_str[:22]  # 提取data头
                base64_bytes_img = str.encode(base64_str[22:])  # 字符串转为字节串
            else:  # 不存在data头
                self.header = DEFAULT_HEADER
                base64_bytes_img = str.encode(base64_str)  # 字符串转为字节串
            # print('Catch Base64 Data Recommend : '+self.header)
        elif (base64_bytes != b''):  #
            self.header = DEFAULT_HEADER
            base64_bytes_img = base64_bytes
        else:
            self.header = DEFAULT_HEADER
            print('Load Base64 Data Fail')

        self.base64_bytes_img = base64_bytes_img  # 保存base64源文件(bytes)
        # self.mat_img = base642mat(base64_bytes_img)  # base64转换为mat
        #下两行作用相同，但第一行强制变换宽高
        # self.mat_img = cv.resize(base642mat(base64_bytes_img),(480,640), interpolation = cv.INTER_NEAREST)#
        self.mat_img = base642mat(base64_bytes_img)#cv.resize(base642mat(base64_bytes_img),(480,640), interpolation = cv.INTER_NEAREST)
    
    #利用捕捉的类型头编码
    def mat2base64_no_header(self):
        if ('PNG' in self.header):
            image = cv.imencode('.png', self.mat_img)[1]
        elif ('JPG' in self.header):
            image = cv.imencode('.jpg', self.mat_img)[1]
        else:
            image = cv.imencode('.png', self.mat_img)[1]
        return str(base64.b64encode(image))[2:-1]

    #利用捕捉的类型头编码
    def mat2base64_with_header(self):
        if ('PNG' in self.header):
            image = cv.imencode('.png', self.mat_img)[1]
        elif ('JPG' in self.header):
            image = cv.imencode('.jpg', self.mat_img)[1]
        else:
            image = cv.imencode('.png', self.mat_img)[1]
        return self.header + str(base64.b64encode(image))[2:-1]



if __name__ == '__main__':
    img_file = cv.imread('../static/1.jpg')  # 二进制打开图片文件
    gray = cv.cvtColor(img_file, cv.COLOR_BGR2GRAY)



#犯了一下午傻逼！！！服了！！！！
#html里面直接接受了本地url,后端response没用，气死了

    # def mat2base64(self, abc):
    #
    #     outfilename = str(uuid.uuid4()) + os.path.splitext(self.temp_image_path)[1]
    #     outfiledir = os.path.split(self.temp_image_path)[0]  # ../static/temp/images
    #     outfilepath = outfiledir + '/' + outfilename  # ../static/temp/images\d8dd148a-c1a9-4972-a659-8ce6870a2ea7.jpg
    #     self.temp_image_path = outfilepath
    #
    #     flag = cv.imwrite(outfilepath,abc)
    #
    #     print(outfilepath)
    #     img_file = open(outfilepath, 'rb')  # 二进制打开图片文件
    #     img_b64encode = base64.b64encode(img_file.read())  # base64编码 img_b64encode : b'/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCg
    #     return img_b64encode
    #
    # # 析构函数
    # def __del__(self):
    #     if (self.temp_image_path != './static/temp/1.png'):
    #         os.remove(self.temp_image_path)