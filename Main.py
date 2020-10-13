from lib.Classifier import RsPhotoClassifier

class MyClassifier(RsPhotoClassifier):
    def classify(self, file_name: str) -> str:
        file_param = file_name[:-5].split('_')
        if file_param[4] == '20':
            return '<% NULL %>'
        return file_param[2] + '/' + file_param[3] + file_param[4]


c = MyClassifier('testData', 'dest')

