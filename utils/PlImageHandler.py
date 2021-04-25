from PIL import Image
import numpy as np
# import matplotlib.pyplot as plt

from pynq import allocate, Overlay,GPIO
from pynq import lib
from pynq.lib.video import *

import cv2 as cv

from tornado import gen
from tornado.concurrent import Future

import time


pl_methods ={
    'Gray':0,
    'Original':1,
    'Sobel':2,
    'Gaussian':3,
    'Canny':5,
}

class my_canny:
    height=512
    width=512
    def __init__(self, bitfile_path,height,width):
        self.bitfile_path = bitfile_path
        self.design=Overlay(bitfile_path)
        self.image_process_ip=self.design.canny_edge_detection_0
        self.image_process_vdma=self.design.axi_vdma_0

        self.height=height
        self.width=width
        self.image_process_vdma.readchannel.mode=VideoMode(width,height,24)
        self.image_process_vdma.readchannel.start()
        self.image_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.image_process_vdma.writechannel.start()
        self.image_frame = self.image_process_vdma.writechannel.newframe()
        self.modify()
        print("modify success" )
    def modify(self,low=50,high=70):
        self.image_process_ip.write(0x10,low)
        self.image_process_ip.write(0x18,high)
        self.image_process_ip.write(0x00,0x81)


    @gen.coroutine
    def write_read(self,plt_image):
        self.image_process_ip.write(0x00,0x81) # start 必须加不然卡死
        self.image_frame = self.image_process_vdma.writechannel.newframe()
        self.image_frame[:]=np.array(plt_image)#original_plt_image#np.array(original_image)
        self.image_process_vdma.writechannel.writeframe(self.image_frame)
        future = Future()
        oldtime=time.time()
        out_frame = self.image_process_vdma.readchannel.readframe()
        plt_image_out = Image.fromarray(out_frame)
        future.set_result(cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR))
        return future# cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)
        # while True:#time.time()-oldtime<1:
        #     if True:#(self.image_process_vdma.readchannel.activeframe == 0):
        #         out_frame = self.image_process_vdma.readchannel.readframe()
        #         plt_image_out = Image.fromarray(out_frame)
        #         return cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)
                # future.set_result(cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR))
                # return future
        # return cv.cvtColor(np.array(plt_image),cv.COLOR_RGB2BGR)
        # future.set_result(cv.cvtColor(np.array(plt_image),cv.COLOR_RGB2BGR))
        # return  future

    def __del__(self):
        self.image_process_vdma.readchannel.stop()
        self.image_process_vdma.writechannel.stop()
        # self.image_process_ip.free()

# bitstream_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','v1_0.bit')
# print(bitstream_path)
canny_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','Canny_1.bit')
# print(canny_path)
# test_path=os.path.join(os.path.abspath("."),'bitstream_files','Canny_1.bit')
canny = my_canny(bitfile_path=canny_path,height=480,width=640)
print(canny.bitfile_path)
frame_width = 640
frame_height = 480



def mat2plt(mat_image):
    plt_image = Image.fromarray(cv.cvtColor(mat_image,cv.COLOR_BGR2RGB))
    #通道变化
    rgba_plt_image=plt_image.convert('RGBA')
    #获取高度宽度
    width, height = plt_image.size
    return rgba_plt_image,width,height



@gen.coroutine
def get_pl_process(plt_image,mode,height,width):
    #转换成fpga可识别的mode
    processed_future = yield canny.write_read(plt_image)
    # if(mode in image_process_methods):
    #     processed_future = yield get_pl_image(plt_image,mode,height,width)
    # else:
    #     processed_future= yield get_canny_image(plt_image,height,width)
    #     print("还未实现")
    return processed_future