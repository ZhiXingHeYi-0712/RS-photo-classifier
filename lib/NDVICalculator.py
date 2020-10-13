import os
import pandas as pd
import numpy as np
import lib.imageNDVI as imvi

class NDVICalculator:
    def __init__(self, origin : str):
        self.origin = origin


    def getNDVI(self):
        first_dir = True
        newDF = None
        for root, dirs, files in os.walk(self.origin):
            file_count = len(files)
            if file_count <= 0:
                continue
            df = pd.DataFrame()
            df['image'] = files
            df['image_datetime'] = df['image'].apply(lambda x: imvi.getDatetimeFromFileName(x)[2])
            df['ndvi'] = df['image'].apply(lambda x: imvi.getNDVIFromFile(root, x))
            if first_dir:  # 第一个目录
                newDF = df
                first_dir = False
            else:
                newDF = newDF.append(df)  # 将其余目录下的所有计算结果合并在一起
        newDF = newDF.set_index('image_datetime')  # 用日期时间作为索引
        nanRow = np.isinf(newDF['ndvi'])
        newDF['ndvi'][nanRow] = np.nan  # 将inf转换为NAN
        newDF = newDF.fillna(method='ffill')  # 用前一天的数值填充空值
        r = newDF.resample('D')  # 按天进行重采样
        meanNDVI = r.mean()  # 计算重采样的均值，即一天之内的多幅图像的平均NDVI
        return meanNDVI


