'''
@Description: 自定义信号集合
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-07-01 11:36:41
'''
from PyQt5.QtCore import pyqtSignal, QObject


#   自定义的信号  完成信号
class CompletionSignal(QObject):
    completed = pyqtSignal(str)


#   获取到cookies  信号
class GetCookiesSignal(QObject):
    getCookies = pyqtSignal(dict)


#   获取到cookies  信号
class NextUrlSignal(QObject):
    nextUrl = pyqtSignal()
