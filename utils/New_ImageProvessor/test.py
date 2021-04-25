#%%
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

from pynq import allocate, Overlay,GPIO
from pynq import lib
from pynq.lib.video import *

import cv2 as cv

# %%
design = Overlay("v1_3.bit")
design?
# %%
