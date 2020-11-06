'''
@Description: 
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-06-12 10:24:36
'''
#   基础库
#   qt5相关
from PyQt5.Qt import QThread
#   selenium相关
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#   自定义信号
import MySignals as MySigs


class MyBrowser(QThread):
    def __init__(self, browser: object, url: str, appid: str, date_ary: tuple):
        super().__init__()
        self.sig = MySigs.GetCookiesSignal()
        self.browser = browser
        self.url = url
        self.appid = appid
        self.date_ary = date_ary

    #   run
    def run(self):
        cookies = {}
        self.browser.set_page_load_timeout(8)
        try:
            self.browser.get(self.url+self.appid)
        except BaseException:
            # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
            self.browser.execute_script("window.stop()")
        #   长等待获取是否获取用户名
        long_wait = WebDriverWait(self.browser, 90)
        login_flag = False
        try:
            login_flag = login_flag or long_wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.tips-wrap')))
        except BaseException:
            pass
        if login_flag:
            cookies = self.browser.get_cookies()
        self.sig.getCookies.emit(cookies, self.appid, self.date_ary)

    # 登录
    # def gameWeixin_lg(self, url: str, appid: str, date_ary: tuple):
    #     cookies = {}
    #     self.browser.set_page_load_timeout(8)
    #     try:
    #         self.browser.get(url+appid)
    #     except BaseException:
    #         # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
    #         self.browser.execute_script("window.stop()")
    #     #   长等待获取是否获取用户名
    #     long_wait = WebDriverWait(self.browser, 90)
    #     login_flag = False
    #     try:
    #         login_flag = login_flag or long_wait.until(
    #             EC.presence_of_element_located(
    #                 (By.CSS_SELECTOR, '.tips-wrap')))
    #     except BaseException:
    #         pass
    #     if login_flag:
    #         cookies = self.browser.get_cookies()
    #     self.sig.getCookies.emit(cookies, appid, date_ary)
