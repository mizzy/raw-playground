#!/usr/bin/env python

import rawpy
raw = rawpy.imread('DSC_3346.NEF')

from matplotlib.pyplot import imshow
img_preview = raw.postprocess(use_camera_wb=True)

imshow(img_preview)

