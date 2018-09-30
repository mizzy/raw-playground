#!/usr/bin/env python
# http://uzusayuu.hatenadiary.jp/entry/2018/09/23/162412

import rawpy
import numpy as np
from matplotlib.pyplot import imshow
import imageio
import math

raw = rawpy.imread('DSC_3346.NEF')

### イメージプレビュー
'''
img_preview = raw.postprocess(use_camera_wb=True)
imshow(img_preview)
'''

### Convert raw data into numpy array
h, w = raw.sizes.raw_height, raw.sizes.raw_width
raw_image = raw.raw_image.copy()
raw_array = np.array(raw_image).reshape((h, w)).astype('float')

### raw array のプレビュー
'''
outimg = raw_array.copy()
outimg = outimg.reshape((h, w))
outimg[outimg < 0] = 0
outimg = outimg / outimg.max()
imshow(outimg, cmap='gray')
'''

### ブラックレベル補正
blc = raw.black_level_per_channel
bayer_pattern = raw.raw_pattern

blc_raw = raw_array.copy()
for y in range(0, h, 2):
    for x in range(0, w, 2):
        colors = [0, 0, 0, 0]
        blc_raw[y + 0, x + 0] -= blc[bayer_pattern[0, 0]]
        blc_raw[y + 0, x + 1] -= blc[bayer_pattern[0, 1]]
        blc_raw[y + 1, x + 0] -= blc[bayer_pattern[1, 0]]
        blc_raw[y + 1, x + 1] -= blc[bayer_pattern[1, 1]]


### ブラックレベル補正後のプレビュー
'''
outimg = blc_raw.copy()
outimg = outimg.reshape((h, w))
outimg[outimg < 0] = 0
outimg = outimg / outimg.max()
imshow(outimg, cmap='gray')
'''

### 簡易デモザイク
dms_img = np.zeros((h//2, w//2, 3))
for y in range(0, h, 2):
    for x in range(0, w, 2):
        colors = [0, 0, 0, 0]
        colors[bayer_pattern[0, 0]] += blc_raw[y + 0, x + 0]
        colors[bayer_pattern[0, 1]] += blc_raw[y + 0, x + 1]
        colors[bayer_pattern[1, 0]] += blc_raw[y + 1, x + 0]
        colors[bayer_pattern[1, 1]] += blc_raw[y + 1, x + 1]
        dms_img[y // 2, x // 2, 0] = colors[0]
        dms_img[y // 2, x // 2, 1] = (colors[1] + colors[3]) / 2
        dms_img[y // 2, x // 2, 2] = colors[2]

### デモザイク後のプレビュー

'''
outimg = dms_img.copy()
outimg = outimg.reshape((h // 2, w //2, 3))
outimg[outimg < 0] = 0
outimg = outimg / outimg.max()
imshow(outimg)
'''

### ホワイトバランス補正
wb = np.array(raw.camera_whitebalance)
img_wb = dms_img.copy().flatten().reshape((-1, 3))

for index, pixel in enumerate(img_wb):
    pixel = pixel * wb[:3] / max(wb)
    img_wb[index] = pixel

### ホワイトバランス補正後のプレビュー
'''
outimg = img_wb.copy()
outimg = outimg.reshape((h // 2, w //2, 3))
outimg[outimg < 0] = 0
outimg = outimg / outimg.max()
imshow(outimg)
'''

### カラーマトリクス補正
color_matrix = np.array([[1024, 0, 0], [0, 1024, 0], [0, 0, 1024]])

img_ccm = np.zeros_like(img_wb)
for index, pixel in enumerate(img_wb):
    pixel = np.dot(color_matrix, pixel)
    img_ccm[index] = pixel

### ガンマ補正
img_gamma = img_ccm.copy().flatten()
img_gamma[img_gamma < 0] = 0
img_gamma = img_gamma/img_gamma.max()
for index, val in enumerate(img_gamma):
    img_gamma[index] = math.pow(val, 1/2.2)
img_gamma = img_gamma.reshape((h//2, w//2, 3))

outimg = img_gamma.copy().reshape((h // 2, w //2, 3))
outimg[outimg < 0] = 0
outimg = outimg * 255
imageio.imwrite("sample.png", outimg.astype('uint8'))
