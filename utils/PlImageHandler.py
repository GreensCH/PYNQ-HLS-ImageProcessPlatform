from PIL import Image
import numpy as np
# import matplotlib.pyplot as plt

from pynq import allocate, Overlay,GPIO
from pynq import lib
from pynq.lib.video import *

import cv2 as cv

from tornado import gen
from tornado.concurrent import Future

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


def mat2plt(mat_image):
    plt_image = Image.fromarray(cv.cvtColor(mat_image,cv.COLOR_BGR2RGB))
    #通道变化
    rgba_plt_image=plt_image.convert('RGBA')
    #获取高度宽度
    width, height = plt_image.size
    return rgba_plt_image,width,height

@gen.coroutine
def get_pl_image(plt_image,model,width,height):
    design = Overlay(bitstream_path)
    image_process_ip = design.ImageProcessor_0
    image_process_vdma = design.axi_vdma_0
#写入内存映射宽高
    #0,1 gray 2sobel 3 gaussian 
    arg1=0
    arg2=0
    image_process_ip.write(0x10,model)
    image_process_ip.write(0x18, height)
    image_process_ip.write(0x20, width)
    image_process_ip.write(0x28, arg1)
    image_process_ip.write(0x30, arg2)
    image_process_ip.write(0x00,0x81) # start 必须加不然卡死

    image_process_vdma.readchannel.model=VideoMode(width,height,32)
    image_process_vdma.readchannel.start()

    image_process_vdma.writechannel.model=VideoMode(width,height,32)
    image_process_vdma.writechannel.start()

    image_frame = image_process_vdma.writechannel.newframe()

    image_frame[:]=np.array(rgba_plt_image)#original_plt_image#np.array(original_image)
    image_process_vdma.writechannel.writeframe(image_frame)

    while True:
        if(image_process_vdma.readchannel.activeframe == 0):
            out_frame = image_process_vdma.readchannel.readframe()
            plt_image_out = Image.fromarray(out_frame)
            break;
    image_process_vdma.readchannel.stop()
    image_process_vdma.writechannel.stop()
    del out_frame
    del image_frame
    design.free()
    mat_img = cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR)
    future = Future()
    future.set_result(mat_img)
    return future

@gen.coroutine
def get_pl_process(plt_image,model,height,width):
    #转换成fpga可识别的mode
    print(model)
    if model == pl_methods["Gray"]:#gray
        print("PLGray")
        processed_future = yield get_pl_image(plt_image,0,height,width)
    elif model == pl_methods["Original"]:#original
        processed_future = yield get_pl_image(plt_image,1,height,width)
    elif model == pl_methods["Sobel"]:#Sobel
        processed_future = yield get_pl_image(plt_image,2,height,width)
    elif model == pl_methods["Gaussian"]:#Gaussian
        processed_future = yield get_pl_image(plt_image,3,height,width)
    elif model == pl_methods["Canny"]:#Canny
        processed_future = yield get_pl_image(plt_image,4,height,width)
    else:
        processed_future = yield get_pl_image(plt_image,0,height,width)
    return processed_future