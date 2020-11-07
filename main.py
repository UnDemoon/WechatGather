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
#   qt5
from PyQt5 import QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import QDate, Qt, QDateTime
#   引入ui文件
from home import Ui_MainWindow as Ui
#   引入浏览器线程类
from MyBrowser import MyBrowser
#   引入api类
from HouyiApi import HouyiApi as Api
#   引入采集类
from GameweixinGather import GameweixinGather as GameGather
#   DB类
from MyDb import MyDb
#   信号类集合
import mySignals as MySigs
#   工具集
import utils as myTools


class MyApp(QtWidgets.QMainWindow, Ui):
    def __init__(self):
        #   UI
        QtWidgets.QMainWindow.__init__(self)
        Ui.__init__(self)
        self.setupUi(self)
        #   属性
        self.db = MyDb()
        self.api = Api()
        self.bar_note = None
        self.browser = None
        self.threadPools = []   # 线程池
        # 方法
        self._initdata()
        self.DateEdit.dateChanged.connect(self._timeInit)
        self.pushButton.clicked.connect(self.start_run)

    #   数据初始化
    def _initdata(self):
        today = QDate.currentDate()
        self.DateEdit.setDate(today)
        self.DateEdit.setCalendarPopup(True)
        self.DateEdit_2.setDate(today.addDays(-5))
        self.DateEdit_2.setEnabled(False)
        self._synDb()

    #   时间处理
    def _timeInit(self):
        endDate = self.DateEdit.date()
        self.DateEdit_2.setDate(endDate.addDays(-5))

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
    def _synDb(self):
        self.listWidget.clear()
        today = QDate.currentDate()
        tuple_uix = myTools.dateToStamps((today, today))
        log_list = self.db.find('update_at', tuple_uix[0], '>=', 'run_log')
        for log in log_list:
            _id, _url, _at = log
            item = QtWidgets.QListWidgetItem()
            update_time = myTools.unixTimeDate(_at)
            item.setText(_url+"    "+update_time.toString('HH:mm:ss'))
            item.setData(1, _id)
            self.listWidget.addItem(item)
        self._barInfo("今日采集总计", str(len(log_list)))

    #   按钮触发
    def start_run(self):
        dates = (self.DateEdit_2.date(), self.DateEdit.date())
        sigGetCookies = MySigs.GetCookiesSignal()
        sigGetCookies.getCookies.connect(self._getCookiesListener)
        # lgm.gameWeixin_lg(browserInit(), sigGetCookies, dates)
        self.browser = MyBrowser(sigGetCookies, dates)
        self.browser.start()

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

    #   获取cookies监听
    def _getCookiesListener(self, info: dict):
        gather = GatherThread(info['appid'], info['cookies'], info['dates'], info['url'])
        self.threadPools.append(gather)
        gather.sig.completed.connect(self._completedListener)
        gather.start()

    #   完成监听
    def _completedListener(self, parm):
        url = parm.strip()
        today = QDate.currentDate()
        tuple_uix = myTools.dateToStamps((today, today))
        sql = '''
        SELECT
            *
        FROM
            run_log
        WHERE
            update_at >= '{0}'
            AND url = '{1}'
        '''.format(str(tuple_uix[0]), url)
        log_list = self.db.runSql(sql)
        if len(log_list) <= 0:
            now = QDateTime.currentDateTime()
            unix_time = now.toSecsSinceEpoch()
            self.db.saveItem([(parm, str(unix_time))], 'run_log')
            QtWidgets.QMessageBox.information(self, '提示', '采集完成！', QtWidgets.QMessageBox.Yes)
            self._synDb()

    #   在bar上显示信息
    def _barInfo(self, title: str = "", content: str = ""):
        if not title and not content:
            self.statusBar.clearMessage()
            if self.bar_note:
                self.statusBar.removeWidget(self.bar_note)
        else:
            self.statusBar.showMessage(title, 0)  # 状态栏本身显示的信息 第二个参数是信息停留的时间，单位是毫秒，默认是0（0表示在下一个操作来临前一直显示）
            if self.bar_note:
                self.bar_note.setText(content)
            else:
                self.bar_note = QtWidgets.QLabel(content)
                self.statusBar.addPermanentWidget(self.bar_note, stretch=0)


# 采集线程
class GatherThread(QThread):
    def __init__(self, appid: str, cookies: dict, dateary: tuple, url: str):
        super().__init__()
        self.appid = appid
        self.cookies = cookies
        self.dateAry = dateary
        self.url = url
        self.sig = MySigs.CompletionSignal()

    def run(self):
        api = Api()
        #   数据采集
        gameGather = GameGather(self.appid, self.cookies, self.dateAry)
        data = gameGather.startRun()
        api.up('add_gamedata', data)
        self.sig.completed.emit(self.url)


# 浏览器开启
# def browserInit():
#     # 实例化一个chrome浏览器
#     chrome_options = webdriver.ChromeOptions()
#     # options.add_argument(".\ChromePortable\App\Chrome\chrome.exe");
#     chrome_options.binary_location = ".\\ChromePortable\\App\\Chrome\\chrome.exe"
#     # chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--headless')
#     # chrome_options.add_argument('--disable-gpu')
#     # browser = webdriver.Chrome(options=chrome_options)
#     browser = webdriver.Chrome(options=chrome_options)
#     # 设置等待超时
#     return browser


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
