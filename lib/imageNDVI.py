# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 08:38:44 2020

@author: quyh2_000
"""
import numpy as np
from skimage import io
import os, re
from datetime import datetime as dtm
from PIL import Image
def contrast_stretch(im):
    """
    Performs a simple contrast stretch of the given image, from 5-100%.
    """
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 100)
    in_min = np.min(im)
    in_max = np.max(im)

    out_min = 0.0
    out_max = 1.0
    
    k = (out_min - out_max) / (in_min - in_max)
    y1 = out_min
    x1 = in_min
    c = y1 - k * x1 

#    out = im - in_min
#    out *= ((out_min - out_max) / (in_min - in_max))
#    out += in_min
    out = im * k + c

    return out

def splitRedNir(img, expose, bWorak = False):
    """
    bWorak = True: 用文献Worak, Sensors,2013,13的公式
    """
    
    img =  img.astype('float')
    img = img/np.sqrt(expose)
    
    b = img[:,:,2] # BLUE AS NIR
    
    g = img[:,:,1]
    
    r = img[:,:,0] # RED + DN
    kb = 0.90
    kg = 0.75
    if bWorak:
        DN_nir = (kb*b + kg*g)/2
        DN_red = r - DN_nir
        
    else:
    
        DN_nir = (b + g)/2
        DN_red = ( r / 2)
    return DN_red, DN_nir
def restoreRGB(awbGains, img):
    """
    restore the original RGB value using awb gains value
    """
    r_gain = awbGains[0]
    b_gain = awbGains[1]
    img[:,:,0] = img[:,:,0]/r_gain
    img[:,:,2] = img[:,:,2]/b_gain
    return img

def extractRedNir(img):
    R = img[:,:,0]
    G = img[:,:,1]
#    B = img[:,:,2]


#    QE_RED = [0.944, 0.186] # Red, Green QE
#    #相机的第一通道和第二通道在近红外波段的波谱响应
#    #QE_NIR = [0.91, 0.88]
#    QE_NIR = [0.92, 0.88]
#    k1 = QE_NIR[0]/QE_NIR[1]
#    k2 = QE_RED[0]/QE_RED[1]


##    nir = (k1 * R - k2 * G)/(k1 - k2)
#    scatter = 0.95  #散射比(部分近红外来自外部散射)
#    nir = nir * scatter
#    red = R - nir 
    k1 = 0.935
    k2 = 0.203
    nir = (G - k2*R) / (k1 - k2)
    red = (k1*R - G) / (k1 - k2)
    red[red < 0] = 0
    return red, nir

def extractRedNir2(img):
#    img =  img.astype('float')
    R = img[:,:,0]
    G = img[:,:,1]
    B = img[:,:,2]
    nir =  (G + B)/2
#    red = R - nir
    
    scatter = 0.95 #散射比(部分近红外来自外部散射)
    nir = nir * scatter
    red = R.astype('float16') - nir #(k2 * R - G) / (k2 - k1)
    red[red < 0] = nir[red < 0] #如果红色小等于零，两种情况：1 - 太暗； 2：太亮
    
#    red = (r1*k1 + r2*k2)/2
#    red = (red0 + red1)/2
#    a = (k1 + k2)/(k1 - k2)
#    b = 2/(k1 - k2)
#    ndvi = a - b * G/R
    return red, nir

def calcaluteNDVI(red,nir,k):
    red = k * red 
    upper = nir - red
    lower = nir + red
    ndvi = np.divide(upper,lower)
#    ndvi = np.multiply(ndvi,nir) # scale ndvi using nir 
#    ndvi[ndvi <= 0 ] = 0
#    ndvi[ndvi > 1 ] = 0
#    ndvi = ndvi * 255
    return ndvi
def readAwbGains(paraFile):
    vals = []
    try:
        fobj=open(paraFile,'r')
    except IOError as e:
        print('Error: Open para file',e)
    else:
        for eachLine in fobj:
            [key,values] = eachLine.split(':')
            if 'awb_gains' == key:
                valList = re.findall(r"\d+\.?\d*",values)
                for v in valList:
                    val = int(v)
                    vals.append(val)
    fobj.close()
    gains = [vals[0]/vals[1], vals[2]/vals[3]]
    return gains
def readImage(fn):
    path,ext = os.path.splitext(fn)
    if 'npy' in ext:
        img = np.load(fn)
    else:
        img = io.imread(fn)
    return img
def stream2ndvi(rawing,awbGains, outFile):
    """
    calculate NDVI from 3-channel streaming (raw)
    output the result file in an image file
    the output image have 3 channels: red, nir and ndvi
    """
    
    img = restoreRGB(awbGains,rawing)
    red,nir = extractRedNir2(img)
    #dn_red,dn_nir = splitRedNir(img, expose,bWorak = True)
    k = 1.0
    ndvi = calcaluteNDVI(red,nir,k)
    
#    ndvi = contrast_stretch(ndvi)
    outImage = img
    outImage[:,:,0] = red
    outImage[:,:,1] = nir
    outImage[:,:,2] = ndvi    
    outImage = outImage.astype('uint8')
    io.imsave(outFile, outImage)
    
def raw2jpeg(rawing,outFile):
    raw = rawing.astype('uint8')
    Image.fromarray(raw).save(outFile)
def detectBoard(image):
    """
    从图像中自动查找参考板
    
    """
    b0 = image[:,:,1]
    thr = np.percentile(b0, 0.6)
    inx = b0 <= thr
    r,g,b = [image[:,:,i] * inx for i in range(3)]
    refBoard = image
    refBoard[:,:,0] = r
    refBoard[:,:,1] = g
    refBoard[:,:,2] = b
    
    return refBoard
    
def detectVegetation(image):
    """
    将图像中属于植被的像元找出来
    """
    r = image[:,:,0]
    g = image[:,:,1]
    b = image[:,:,2]
    gi = 2.0*g - r - b
    thr = np.percentile(gi,85)
#    r[gi < thr] = 0
#    g[gi < thr] = 0
#    b[gi < thr] = 0
#    vegClass = image
#    vegClass[:,:,0] = r
#    vegClass[:,:,1] = g
#    vegClass[:,:,2]= b
    vegIndex = gi > thr
    return vegIndex
def findNearestTime(times,t):
    delta = abs(times - t)
    beforeSort = delta.copy()
    beforeSort.sort()
    res = beforeSort[1]
    nearestTime = times[np.where(delta == res)]
    return nearestTime[0]
    

def getDatetimeFromFileName(fn):
    """
    从文件名中提取图像拍摄日期
    
    输入参数
    ----------
    fn : TYPE，String
        文件名称，不包含目录.

    输出参数
    -------
    strDate : TYPE，字符串类型的文件日期
        从文件名中提取到的字符串类型的日期
    dtDate : TYPE，datetime类型
        从文件名中提取到的日期类型类型的日期，方便日期比较

    """
    splitted = fn.split('_')
    y,m,d = splitted[2:5]
    strDate = '{:0>4d}_{:0>2d}_{:0>2d}'.format(int(y),int(m),int(d))
    dtDate = dtm.strptime(strDate, '%Y_%m_%d')
    strTime = splitted[5].split('.')[0]
    strDateTime = strDate + ' ' + strTime
    dtDatetime = dtm.strptime(strDateTime, '%Y_%m_%d %H%M%S')
    return strDate, dtDate, dtDatetime

def getNDVIFromFile(root,name):
    """
    根据图像文件名，读取图像数据，并计算图像的NDVI

    Parameters
    ----------
    root : TYPE，字符串
        图像所在的路径.
    name : TYPE，字符串
        文件名称

    Returns
    -------
    ndvi : TYPE，numpy类型实数
        计算得到的图像的NDVI均值

    """
    fullName = os.path.join(root, name)
    img = io.imread(fullName)
    red,nir = splitRedNir(img = img, expose = 1, bWorak = True)
    ndvi = (nir - red)/(nir + red)
    ndvi = np.mean(ndvi)
    return ndvi

