from PIL import Image
import numpy as np
# import matplotlib.pyplot as plt

from pynq import allocate, Overlay,GPIO
from pynq import lib
from pynq.lib.video import *

import cv2 as cv

from tornado import gen
from tornado.concurrent import Future
from tornado.gen import Return

import time

pl_methods_dict = {
    'Original':0,
    'Gray':1,
    'Sobel':2,
    'Gaussian':3,
    'Sharpen':4,
    'Dilate':5,
    'Erode':6,
    'Negative':7,
    'Median':-1,
}

pl_methods = pl_methods_dict.keys()



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


class my_image_processor:
    height=10
    width=10
    mode=0
    def __init__(self, bitfile_path,height,width):
        self.bitfile_path = bitfile_path
        self.design=Overlay(bitfile_path)
        self.image_process_ip=self.design.ImageProcessor_0
        self.image_process_vdma=self.design.axi_vdma_0
        self.medianblur_process_ip=self.design.ImageProcessHandler_2_0
        self.medianblur_process_vdma=self.design.axi_vdma_1

        self.height=height
        self.width=width
        self.image_process_vdma.readchannel.mode=VideoMode(width,height,32)
        self.image_process_vdma.readchannel.start()
        self.image_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.image_process_vdma.writechannel.start()
        self.image_frame = self.image_process_vdma.writechannel.newframe()

        self.medianblur_process_vdma.readchannel.mode=VideoMode(width,height,24)
        self.medianblur_process_vdma.readchannel.start()
        self.medianblur_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.medianblur_process_vdma.writechannel.start()
        self.medianblur_frame = self.medianblur_process_vdma.writechannel.newframe()

        self.modify(height=height,width=width)
        print("modify success" )
    def modify(self,mode = 0 ,height=480,width=640):
        self.image_process_ip.write(0x10,mode)
        self.image_process_ip.write(0x18,height)
        self.image_process_ip.write(0x20,width)
        self.image_process_ip.write(0x00,0x81)
        self.medianblur_process_ip.write(0x10,mode)
        self.medianblur_process_ip.write(0x18,height)
        self.medianblur_process_ip.write(0x20,width)
        self.medianblur_process_ip.write(0x00,0x81)

    def modify_mode(self,mode = 0):
        self.mode=mode
        self.image_process_ip.write(0x10,mode)

    def modify_median_size(self,height,width):
        del self.medianblur_frame
        self.medianblur_process_vdma.readchannel.mode=VideoMode(width,height,24)
        self.medianblur_process_vdma.readchannel.start()
        self.medianblur_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.medianblur_process_vdma.writechannel.start()
        self.medianblur_frame = self.medianblur_process_vdma.writechannel.newframe()
        self.medianblur_process_ip.write(0x18,height)
        self.medianblur_process_ip.write(0x20,width) 

    def modify_size(self,height=480,width=640):
        # print("modify_size：height %d width %d"%(height,width))
        self.height=height
        self.width=width
        del self.image_frame
        self.medianblur_process_ip.write(0x00,0x81)
        self.image_process_ip.write(0x20,width)
        self.image_process_ip.write(0x18,height)
        self.image_process_vdma.readchannel.mode=VideoMode(width,height,32)
        self.image_process_vdma.readchannel.start()
        self.image_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.image_process_vdma.writechannel.start()
        self.image_frame = self.image_process_vdma.writechannel.newframe()
 
        del self.medianblur_frame
        self.medianblur_process_ip.write(0x00,0x81)
        self.medianblur_process_ip.write(0x18,height)
        self.medianblur_process_ip.write(0x20,width)  
        self.medianblur_process_vdma.readchannel.mode=VideoMode(width,height,24)
        self.medianblur_process_vdma.readchannel.start()
        self.medianblur_process_vdma.writechannel.mode=VideoMode(width,height,32)
        self.medianblur_process_vdma.writechannel.start()
        self.medianblur_frame = self.medianblur_process_vdma.writechannel.newframe()

    def nogen_median_write_read(self,plt_image):
        self.medianblur_frame[:]=plt_image#np.array(plt_image)#original_plt_image#np.array(original_image)
        self.medianblur_process_vdma.writechannel.writeframe(self.medianblur_frame)
        # future = Future()
        _out_frame = self.medianblur_process_vdma.readchannel.readframe()
        raise cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR)
    def nogen_write_read(self,plt_image):
        self.image_frame[:]=plt_image#np.array(plt_image)#original_plt_image#np.array(original_image)
        self.image_process_vdma.writechannel.writeframe(self.image_frame)
        # future = Future()
        _out_frame = self.image_process_vdma.readchannel.readframe()
        # future.set_result(cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR))
        return cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR)

    @gen.coroutine
    def median_write_read(self,plt_image):
        self.medianblur_frame[:]=plt_image#np.array(plt_image)#original_plt_image#np.array(original_image)
        self.medianblur_process_vdma.writechannel.writeframe(self.medianblur_frame)
        # future = Future()
        _out_frame = self.medianblur_process_vdma.readchannel.readframe()
        raise Return(cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR))
        # future.set_result(cv.cvtColor(out_frame,cv.COLOR_RGB2BGR))
        # return future

    @gen.coroutine
    def write_read(self,plt_image):
        self.image_frame[:]=plt_image#np.array(plt_image)#original_plt_image#np.array(original_image)
        self.image_process_vdma.writechannel.writeframe(self.image_frame)
        # future = Future()
        _out_frame = self.image_process_vdma.readchannel.readframe()
        # future.set_result(cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR))
        raise Return(cv.cvtColor(_out_frame,cv.COLOR_RGB2BGR))
        # return future
        # return cv.cvtColor(out_frame,cv.COLOR_RGB2BGR)#cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)

    def __del__(self):
        self.image_process_vdma.readchannel.stop()
        self.image_process_vdma.writechannel.stop()
        self.medianblur_process_vdma.readchannel.stop()
        self.medianblur_process_vdma.writechannel.stop()
        # self.image_process_ip.free()

canny_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','Canny_1.bit')
# image_processor_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','image_processor_v1.bit')
image_processor_path = os.path.join('/home/xilinx/jupyter_notebooks/app/PYNQ-HLS-ImageProcessPlatform','utils','bitstream_files','HLSImageProcessor_3.bit')
# image_processor_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','HLSImageProcessor_2.bit')
# print(canny_path)
# test_path=os.path.join(os.path.abspath("."),'bitstream_files','Canny_1.bit')
frame_width = 640
frame_height = 480
# canny = my_canny(bitfile_path=canny_path,height=frame_height,width=frame_width)
print(image_processor_path)
image_process = my_image_processor(bitfile_path=image_processor_path,height=frame_height,width=frame_width)

# print(image_process.bitfile_path)

def init_ip():
    global image_process
    image_process = my_image_processor(bitfile_path=image_processor_path,height=frame_height,width=frame_width)

def ip_active():
    try: 
        type (eval(image_process)) 
    except: 
        return  False 
    else: 
        return  True 


def release_ip_mode():
    global image_process,canny
    del image_process
    del canny

def reload_ip_mode():
    canny = my_canny(bitfile_path=canny_path,height=frame_height,width=frame_width)
    image_process = my_image_processor(bitfile_path=image_processor_path,height=frame_height,width=frame_width)

def modify_pl_image_processor(mode=0):
    image_process.modify_mode(pl_methods_dict[mode])
def modify_pl_image_processor2(mode=0):
    image_process.modify_mode(mode)
def modify_size_pl_image_processor(height,width):
    image_process.modify_size(height=height,width=width)

def mat2plt(mat_image):
    plt_image = Image.fromarray(cv.cvtColor(mat_image,cv.COLOR_BGR2RGB))
    #通道变化
    rgba_plt_image=plt_image.convert('RGBA')
    #获取高度宽度
    width, height = plt_image.size
    return rgba_plt_image,width,height


def get_pl_size():
    return image_process.width,image_process.height
def get_pl_height():
    return image_process.height
def get_pl_width():
    return image_process.width

def get_pl_mode():
    return image_process.mode

@gen.coroutine
def get_pl_process(plt_image,mode,height,width):
    #转换成fpga可识别的mode
    if(mode!='Median'):
        processed_future = yield image_process.write_read(plt_image)
    else:
        processed_future = yield image_process.median_write_read(plt_image)
    # processed_future = yield image_process.write_read(plt_image)
    return processed_future


def nogen_get_pl_process(plt_image,mode,height,width):
    #转换成fpga可识别的mode
    time_start=time.time()
    original_mode=get_pl_mode()
    modify_size_pl_image_processor(height=height,width=width)
    modify_pl_image_processor(mode)
    if(mode!='Median'):
        processed_future =  image_process.nogen_write_read(plt_image)
    else:
        processed_future =  image_process.nogen_median_write_read(plt_image)
    # processed_future = yield image_process.write_read(plt_image)
    modify_pl_image_processor2(original_mode)
    return processed_future,time.time()-time_start

