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
from PyQt5.QtCore import pyqtSignal, QObject, QDate, Qt, QSize, QMimeData
#   引入ui文件
from home import Ui_MainWindow as Ui
#   引入登录模块
import login as lgm
#   引入requests类
from HouyiApi import HouyiApi as Api
from GameweixinGather import GameweixinGather as GameGather
from MyDb import MyDb
import utils as myTools


class MyApp(QtWidgets.QMainWindow, Ui):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.db = MyDb()
        self.api = Api()
        self.bar_note = []
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
        # self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        for idx, acc in enumerate(data):
            _id, appid, app_name, check = acc
            item = QtWidgets.QListWidgetItem()
            item.setText(str(idx+1) + "     "+app_name)
            if int(check) == 1:
                item.setCheckState(Qt.CheckState(2))
            else:
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
        self._barInfo("提示", "同步中，请稍后！")
        self.db.clear()
        res = self.api.pageData('adv_apps')
        tuple_list = []
        for item in res['Result'].get('List', []):
            tuple_list.append((item['wx_appid'], item['name'], 0))
        self.db.saveItem(tuple_list)
        self._initdata()
        QtWidgets.QMessageBox.information(self, '提示', '同步完成！', QtWidgets.QMessageBox.Yes)
        self._barInfo()

    #   按钮触发
    def start_run(self):
        dates = (self.DateEdit_2.date(), self.DateEdit.date())
        select_list = []
        items_len = self.listWidget.count()
        for index in range(0, items_len):
            if self.listWidget.item(index).checkState() == Qt.CheckState(2):
                select_list.append(self.listWidget.item(index).data(1))
        self._checkByAry(select_list)
        # self.browser, wait = browserInit()
        # while len(select_list) > 0:
        #     appid = select_list.pop()
        #     cookies = lgm.gameWeixin_lg(self.browser, URL['login'] + appid, wait)
        #     if not cookies:
        #         QtWidgets.QMessageBox.warning(self, '错误', '获取登录信息失败', QtWidgets.QMessageBox.Yes)
        #     myTools.logFile(json.dumps(cookies))
        #     gather = GatherThread(appid, cookies, dates)
        #     gather.start()

        cookies = [{"domain": ".game.weixin.qq.com", "expiry": 1604566673, "httpOnly": "true", "name": "oauth_sid", "path": "/", "secure": "false", "value": "BgAAB-EX9dJUSvoFN5fpHu5SK-sdRj-DL5oHXU8gSwrUbMc"}]
        appid = 'wx99d027c04ebc093c'
        gather = GatherThread(appid, cookies, dates)
        gather.start()

    #   根据appid更新check状态
    def _checkByAry(self, appid_ary: list):
        sql = '''
            UPDATE app_info
            SET `check_state`= 0
        '''
        self.db.runSql(sql)
        #   处理特殊情况 只有一个元素的元组转字符串时多一个 ,
        appid_ary_str = "('" + appid_ary[0] + "')" if len(appid_ary) == 1 else str(tuple(appid_ary))
        sql = '''
        UPDATE app_info
        SET `check_state`= 1
        WHERE
            appid IN
            {0}
        '''.format(appid_ary_str)
        self.db.runSql(sql)

    #   在bar上显示信息
    def _barInfo(self, title: str = "", content: str = ""):
        if not title and not content:
            self.statusBar.clearMessage()
            for wt in self.bar_note:
                # self.statusBar.removeWidget(wt)
                wt.setText("ssddsd")
        else:
            self.statusBar.showMessage(title, 0)  # 状态栏本身显示的信息 第二个参数是信息停留的时间，单位是毫秒，默认是0（0表示在下一个操作来临前一直显示）
            comNum = QtWidgets.QLabel(content)
            self.bar_note.append(comNum)
            self.statusBar.addPermanentWidget(comNum, stretch=0)


#   自定义的信号  完成信号
class CompletionSignal(QObject):
    completed = pyqtSignal(str)


# 采集线程
class GatherThread(QThread):
    def __init__(self, appid: str, cookies: dict, dateary: tuple):
        super().__init__()
        self.appid = appid
        self.cookies = cookies
        self.dateAry = dateary
        self.sig = CompletionSignal()

    def run(self):
        api = Api()
        #   开发平台数据采集
        gameGather = GameGather(self.appid, self.cookies, self.dateAry)
        data = gameGather.startRun()
        print(json.dumps(data))
        self.sig.completed.emit(None)


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
        "login": "https://game.weixin.qq.com/cgi-bin/minigame/static/channel_side/login.html?appid=",
    }
    try:
        RUN_EVN = sys.argv[1]
    except Exception:
        pass
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
