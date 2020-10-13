import os, shutil


class RsPhotoClassifier:
    '''
    分类器。
    需要先继承此类，然后重写classify()函数，最后调用start()函数。
    下面给出一个例子：
    <code>
        from Classifier import RsPhotoClassifier

        class MyClassifier(RsPhotoClassifier):
            def classify(self, file_name: str) -> str:
                file_param = file_name[:-5].split('_')
                if file_param[4] == '20':
                    return '<% NULL %>'
                return file_param[2]+'/'+file_param[3]+file_param[4]

        c = MyClassifier('testData', 'dest')
        c.start()
    </code>
    '''

    def __init__(self, origin: str, dest: str):
        '''
        初始化分类器
        :param origin: 源文件夹相对路径
        :param dest: 目标文件夹相对路径
        '''
        self.origin = origin
        self.dest = dest


    def classify(self, file_name: str) -> str:
        '''
        分类函数。(需要重写)
        例如：文件2096_nirraw_2020_07_14_photo.jpeg需要归入文件夹20200714.
        则需要使file_name=2096_nirraw_2020_07_14_photo.jpeg时函数返回值为20200714.
        如果不需要复制这个文件，请返回'<% NULL %>'
        支持使用多级路径。
        下面给出一个例子：
        <code>
            def classify(self, file_name: str) -> str:
                file_param = file_name[:-5].split('_')
                if file_param[4] == '20':
                    return '<% NULL %>'
                return file_param[2]+'/'+file_param[3]+file_param[4]
        </code>
        :param file_name: 文件名
        :return: 类别名
        '''
        return 'default'


    def start(self):
        current = os.getcwd()
        fileList: list = os.listdir(self.origin)
        for f in fileList:
            clazz: str = self.classify(f)
            if clazz == '<% NULL %>':
                continue
            if clazz == None:
                destPath = self.dest
            else:
                destPath = os.path.join(self.dest, clazz)

            if not os.path.isdir(destPath):
                os.makedirs(destPath)

            shutil.copy(os.path.join(current, self.origin, f), os.path.join(current, destPath))

