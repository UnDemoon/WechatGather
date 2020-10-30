'''
@Description:
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-07-01 11:13:46
'''
#  基础模块
import sys
import time
import json
#   selenium相关
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
#   qt5
from PyQt5 import QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import pyqtSignal, QObject, QDate, Qt, QSize, QItemSelectionModel
#   引入ui文件
from home import Ui_MainWindow as Ui
#   引入登录模块
import login as lgm
#   引入requests类
# from OppoGather import OppoGather as OppoGer
# from VivoGather import VivoGather as VivoGer
# from BdSpider import BdSpider as ToutiaoGer
from HouyiApi import HouyiApi as Api
from MyDb import MyDb
import utils as myTools


class MyApp(QtWidgets.QMainWindow, Ui):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.db = MyDb()
        self.api = Api()
        self.browser = None
        self.threadPools = []
        Ui.__init__(self)
        self.setupUi(self)
        self._initdata()
        self.listWidget.itemClicked.connect(self._onoffCheck)
        self.pushButton_2.clicked.connect(self._clearCheck)
        self.lineEdit.textChanged.connect(self._search)
        self.DateEdit.dateChanged.connect(self._timeInit)
        self.pushButton_3.clicked.connect(self._synHouyi)
        self.pushButton.clicked.connect(self.start_run)

    #   数据初始化
    def _initdata(self):
        data = self.db.listApps()
        self.listWidget.clear()
        self.listWidget.setSelectionModel(QItemSelectionModel(QtWidgets.QAbstractItemView.SelectRows()))
        for idx, acc in enumerate(data):
            _id, appid, app_name, check = acc
            item = QtWidgets.QListWidgetItem()
            item.setText(str(idx+1) + "     "+app_name)
            item.setCheckState(Qt.CheckState(0))
            item.setData(1, appid)
            self.listWidget.addItem(item)
        today = QDate.currentDate()
        self.DateEdit.setDate(today)
        self.DateEdit.setCalendarPopup(True)
        self.DateEdit_2.setDate(today.addDays(-5))
        self.DateEdit_2.setEnabled(False)

    #   时间处理
    def _timeInit(self):
        endDate = self.DateEdit.date()
        self.DateEdit_2.setDate(endDate.addDays(-5))

    # 处理点击
    def _onoffCheck(self, click_item: QtWidgets.QListWidgetItem):
        state = 2 if int(click_item.checkState()) == 0 else 0
        click_item.setCheckState(Qt.CheckState(state))
        return True

    #   清楚所有选项
    def _clearCheck(self):
        items_len = self.listWidget.count()
        for index in range(0, items_len):
            self.listWidget.item(index).setCheckState(Qt.CheckState(0))

    #   搜索功能
    def _search(self, text: str):
        item_list = self.listWidget.findItems(text, Qt.MatchContains)
        if len(item_list) > 0:
            self.listWidget.scrollToItem(item_list[0],  QtWidgets.QAbstractItemView.PositionAtTop)

    #   同步功能
    def _synHouyi(self):
        self.db.clear()
        res = self.api.pageData('list_apps')
        tuple_list = []
        for item in res['Result'].get('List', []):
            tuple_list.append((item['appid'], item['app_name'], 0))
        self.db.saveItem(tuple_list)
        self._initdata()

    #   按钮触发
    def start_run(self):
        dates = (self.DateEdit_2.date(), self.DateEdit.date())
        selected_list = self.listWidget.selectedItems()
        for item in selected_list:
            print(item.text())


# 浏览器开启
def browserInit():
    # 实例化一个chrome浏览器
    chrome_options = webdriver.ChromeOptions()
    # options.add_argument(".\ChromePortable\App\Chrome\chrome.exe");
    chrome_options.binary_location = ".\\ChromePortable\\App\\Chrome\\chrome.exe"
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # browser = webdriver.Chrome(options=chrome_options)
    browser = webdriver.Chrome(options=chrome_options)
    # 设置等待超时
    wait = WebDriverWait(browser, 5)
    return (browser, wait)


if __name__ == '__main__':
    # 定义为全局变量，方便其他模块使用
    global URL, RUN_EVN
    # 登录界面的url
    # https://open.oppomobile.com
    now = time.localtime()
    t = time.strftime("%Y%m%d%H%M", now)
    URL = {
        "oppo_1": "https://id.heytap.com/index.html",
        "oppo_2": "https://id.oppo.com/index.html",
        "vivo": "https://id.vivo.com.cn/?callback=https://dev.vivo.com.cn/home&_"+t+"#!/access/login",
        "toutiao": "https://microapp.bytedance.com/",
    }
    try:
        RUN_EVN = sys.argv[1]
    except Exception:
        pass
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
