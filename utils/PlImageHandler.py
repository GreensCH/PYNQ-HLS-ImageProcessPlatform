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
    'Original':0,
    'Sobel':2,
    'Gaussian':3,
    'Canny':4,
}

bitstream_path = os.path.join(os.path.abspath("."),'utils','bitstream_files','HLSImageProcessor.bit')
print(bitstream_path)
design = Overlay(bitstream_path)
image_process_ip = design.ImageProcessor_0
image_process_vdma = design.axi_vdma_0
canny_vdma = design.axi_vdma_1
canny_ip = design.canny_edge_detection_0
def loadbitstream():
    design = Overlay(bitstream_path)
    image_process_ip = design.ImageProcessor_0
    image_process_vdma = design.axi_vdma_0
    canny_vdma = design.axi_vdma_1
    canny_ip = design.canny_edge_detection_0
def resetbitstream():
    design.free()

def mat2plt(mat_image):
    plt_image = Image.fromarray(cv.cvtColor(mat_image,cv.COLOR_BGR2RGB))
    #通道变化
    rgba_plt_image=plt_image.convert('RGBA')
    #获取高度宽度
    width, height = plt_image.size
    return rgba_plt_image,width,height

image_process_methods=['Gray','Original','Sobel','Gaussian']
def get_pl_image(plt_image,name,width,height):
    
    mode=pl_methods[name]#获取方法
    #写入内存映射宽高
    #0,1 gray 2sobel 3 gaussian 
    arg1=0
    arg2=0
    image_process_ip.write(0x10,mode)
    image_process_ip.write(0x18, height)
    image_process_ip.write(0x20, width)
    image_process_ip.write(0x28, arg1)
    image_process_ip.write(0x30, arg2)
    image_process_ip.write(0x00,0x81) # start 必须加不然卡死
    #640*480
    image_process_vdma.readchannel.mode=VideoMode(width,height,32)
    image_process_vdma.readchannel.start()

    image_process_vdma.writechannel.mode=VideoMode(width,height,32)
    image_process_vdma.writechannel.start()

    image_frame = image_process_vdma.writechannel.newframe()

    image_frame[:]=np.array(plt_image)#original_plt_image#np.array(original_image)
    image_process_vdma.writechannel.writeframe(image_frame)

    oldtime=time.time()
    while time.time()-oldtime<1:
        if(image_process_vdma.readchannel.activeframe == 0):
            out_frame = image_process_vdma.readchannel.readframe()
            plt_image_out = Image.fromarray(out_frame)
            image_process_vdma.readchannel.stop()
            image_process_vdma.writechannel.stop()
            del out_frame
            del image_frame
            return cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)

    
    # mat_img = cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)

    return  cv.cvtColor(np.array(plt_image),cv.COLOR_RGB2BGR)




def mat2plt(mat_image):
    plt_image = Image.fromarray(cv.cvtColor(mat_image,cv.COLOR_BGR2RGB))
    #通道变化
    rgba_plt_image=plt_image.convert('RGBA')
    #获取高度宽度
    width, height = plt_image.size
    return rgba_plt_image,width,height

def get_canny_image(plt_image,width,height):
    #写入内存映射宽高
    hist_hthr=50
    hist_lthr=80
    canny_ip.write(0x10,hist_hthr)
    canny_ip.write(0x18, hist_lthr)
    canny_ip.write(0x00,0x81) # start 必须加不然卡死

    canny_vdma.readchannel.mode=VideoMode(width,height,24)
    canny_vdma.readchannel.start()

    canny_vdma.writechannel.mode=VideoMode(width,height,32)
    canny_vdma.writechannel.start()

    image_frame = canny_vdma.writechannel.newframe()

    image_frame[:]=np.array(plt_image)#original_plt_image#np.array(original_image)
    canny_vdma.writechannel.writeframe(image_frame)

    oldtime=time.time()
    while time.time()-oldtime<1:
        # print(time.time()-oldtime)
        if(canny_vdma.readchannel.activeframe == 0):
            out_frame = canny_vdma.readchannel.readframe()
            plt_image_out = Image.fromarray(out_frame)
            canny_vdma.readchannel.stop()
            canny_vdma.writechannel.stop()
            del out_frame
            del image_frame
            return cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)

    
    # mat_img = cv.cvtColor(np.array(plt_image_out),cv.COLOR_RGB2BGR)

    return  cv.cvtColor(np.array(plt_image),cv.COLOR_RGB2BGR)

def get_pl_process(plt_image,mode,height,width):
    #转换成fpga可识别的mode
    if(mode in image_process_methods):
        processed_future =  get_pl_image(plt_image,mode,height,width)
    else:
        processed_future=get_canny_image(plt_image,height,width)
        # print("还未实现")
    return processed_future