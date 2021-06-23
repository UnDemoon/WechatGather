"""
@Description:

@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-02-20 10:25:09
"""
#  基础模块
import sys
import time

#   qt5
from PyQt5 import QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import QDate, Qt, QDateTime
from PyQt5.QtGui import QColor

#   信号类集合
import mySignals as MySigs
#   工具集
import utils as mytools
#   引入采集类
from GameweixinGather import GameweixinGather as GameGather
#   引入api类
from HouyiApi import HouyiApi as Api
#   引入浏览器线程类
from MyBrowser import MyBrowser
#   DB类
from MyDb import MyDb
#   引入ui文件
from home import Ui_MainWindow as Ui


# logging.basicConfig(level=0)


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
        self.run_urls = []  # 要采集的url集合
        self.threadPools = []  # 线程池
        self.sig_change_url = MySigs.ChangeUrlSignal()  # 改变url信号
        # 方法
        self._initData()
        self.listWidget.itemClicked.connect(self._onOffCheck)
        self.DateEdit.dateChanged.connect(self._timeInit)
        self.lineEdit_search.textChanged.connect(self._search)
        self.pushButton_3.clicked.connect(lambda: self._changeAllCheck(0))
        self.pushButton_4.clicked.connect(lambda: self._changeAllCheck(2))
        self.pushButton_5.clicked.connect(self._delChecked)
        self.pushButton_2.clicked.connect(self.autoRun)
        self.pushButton.clicked.connect(self.start_run)

    #   数据初始化
    def _initData(self):
        today = QDate.currentDate()
        self.DateEdit.setDate(today)
        self.DateEdit.setCalendarPopup(True)
        self.DateEdit_2.setDate(today.addDays(-5))
        self.DateEdit_2.setEnabled(False)
        self.checkBox.setCheckState(2)
        self._synDb()

    #   时间处理
    def _timeInit(self):
        end_date = self.DateEdit.date()
        self.DateEdit_2.setDate(end_date.addDays(-5))

    #   清楚所有选项 0全不选 2全选
    def _changeAllCheck(self, check_state: int):
        items_len = self.listWidget.count()
        for index in range(0, items_len):
            self.listWidget.item(index).setCheckState(Qt.CheckState(check_state))

    #   删除选择项
    def _delChecked(self):
        select_list = []
        items_len = self.listWidget.count()
        for index in range(0, items_len):
            if self.listWidget.item(index).checkState() == Qt.CheckState(2):
                select_list.append(self.listWidget.item(index).data(1))
        if len(select_list) <= 0:
            return True
        #   操作数据库
        ids_str = "(" + str(select_list[0]) + ")" if len(select_list) == 1 else str(tuple(select_list))
        sql = '''
        DELETE
        FROM
            {0}
        WHERE
            {1} IN {2}
        '''.format('run_log', 'id', ids_str)
        self.db.runSql(sql)
        self._synDb()
        self._changeAllCheck(0)

    #   搜索功能
    def _search(self, text: str):
        item_list = self.listWidget.findItems(text, Qt.MatchContains)
        if len(item_list) > 0:
            self.listWidget.scrollToItem(item_list[0], QtWidgets.QAbstractItemView.PositionAtTop)

    # 处理点击
    @staticmethod
    def _onOffCheck(click_item: QtWidgets.QListWidgetItem):
        state = 2 if int(click_item.checkState()) == 0 else 0
        click_item.setCheckState(Qt.CheckState(state))
        return True

    #   同步功能
    def _synDb(self):
        #   获取今天时间戳
        today_uix = QDateTime(QDate.currentDate()).toSecsSinceEpoch()
        self.listWidget.clear()
        sql = '''
            SELECT
                *
            FROM
                run_log
            GROUP BY
                url
            ORDER BY
            `id` ASC
            '''.format(today_uix)
        log_list = self.db.runSqlRes(sql)
        for idx, log in enumerate(log_list):
            _id, _name, _appid, _at = log
            item = QtWidgets.QListWidgetItem()
            update_time = mytools.unixTimeDate(_at)
            _url = 'https://game.weixin.qq.com/cgi-bin/minigame/static/channel_side/index.html?appid=' + _appid
            item.setData(99, _url)
            item.setData(1, _id)
            item.setText(
                str(idx) + "    " + _name + "   " + _url + "    " + update_time.toString('yyyy-MM-dd HH:mm:ss'))
            if int(_at) > today_uix:
                item.setBackground(QColor('silver'))
                item.setCheckState(Qt.CheckState(0))
            else:
                item.setCheckState(Qt.CheckState(2))
            self.listWidget.addItem(item)
        # self._barInfo("今日采集总计", str(len(log_list)))

    #   下一个
    def _nextUrl(self, url: str):
        self.sig_change_url.changeUrl.emit(url)

    #   按钮触发
    def start_run(self):
        self.run_urls = []
        if self.browser:
            self.browser.closeBrowser()
        init_url = ''
        #   获取时间
        dates = (self.DateEdit_2.date(), self.DateEdit.date())
        #   判断运行类型
        if self.checkBox.isChecked():
            select_list = []
            items_len = self.listWidget.count()
            for index in range(0, items_len):
                if self.listWidget.item(index).checkState() == Qt.CheckState(2):
                    select_list.append(self.listWidget.item(index).data(99))
            self.run_urls = select_list
            init_url = self.run_urls.pop()
        #   定义信号 链接槽函数
        sig_get_cookies = MySigs.GetCookiesSignal()
        sig_get_cookies.getCookies.connect(self._getCookiesListener)
        self.browser = MyBrowser(sig_get_cookies, dates, init_url)
        self.sig_change_url.changeUrl.connect(self.browser.changeUrl)
        self.browser.start()

    #   自动运行
    def autoRun(self):
        if len(self.run_urls) > 0:
            url = self.run_urls.pop()
            self._nextUrl(url)
        else:
            self._nextUrl("data:,")
            QtWidgets.QMessageBox.information(self, '提示', '没有了！', QtWidgets.QMessageBox.Yes)

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
        if not info:
            self.autoRun()
        else:
            gather = GatherThread(info['appid'], info['cookies'], info['dates'], info['url'])
            self.threadPools.append(gather)
            gather.sig_show_info.showInfo.connect(lambda: self.bar_note)
            gather.sig_completion.completed.connect(self._completedListener)
            gather.start()

    #   完成监听
    # parm = {
    #     "url": "",
    #     "appid": ""
    # }
    def _completedListener(self, parm: dict):
        url = parm['appid']
        app_name = ''
        #   查询appid对应游戏名称
        res = self.api.up('adv_apps', [parm['appid']])
        for app_info in res['Result']['List']:
            if app_info['wx_appid'] == parm['appid']:
                app_name = app_info['name']
        sql = '''
        SELECT
            *
        FROM
            run_log
        WHERE
            url = '{0}'
        '''.format(url)
        log_list = self.db.runSqlRes(sql)
        if len(log_list) <= 0:
            unix_time = QDateTime.currentDateTime().toSecsSinceEpoch()
            self.db.saveItem([(app_name, parm['appid'], str(unix_time))], 'run_log')
            self._synDb()
        else:
            _id = log_list[0][0]
            unix_time = QDateTime.currentDateTime().toSecsSinceEpoch()
            sql = '''
            UPDATE run_log
            SET app_name = '{0}',
                update_at = '{1}'
            WHERE
                id = '{2}'
            '''.format(app_name, unix_time, _id)
            self.db.runSql(sql)
            self._synDb()
        self.autoRun()

    #   在bar上显示信息
    def _barInfo(self, title: str = ""):
        content = ''
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
        self.sig_completion = MySigs.CompletionSignal()

    def run(self):
        api = Api()
        #   数据采集
        game_gather = GameGather(self.appid, self.cookies, self.dateAry)
        data = game_gather.startRun()
        api.up('add_gamedata', data)
        self.sig_completion.completed.emit({
            'url': self.url,
            'appid': self.appid,
        })


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
