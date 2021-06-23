"""
@Description:  浏览器线程
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-06-09 12:04:41
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import utils as mytools
from PyQt5.Qt import QThread
from selenium import webdriver

from mySignals import GetCookiesSignal


class MyBrowser(QThread):
    def __init__(self, sig_cookies: GetCookiesSignal, date_ary: tuple, init_url: str = ''):
        super().__init__()
        self.sig = sig_cookies
        self.date_ary = date_ary
        self.browser = None
        self.init_url = init_url

    #   下一个url
    def changeUrl(self, url: str):
        self.browser.get(url)

    #   run
    def run(self):
        self.browser = self.browserInit()
        if self.init_url:
            self.browser.get(self.init_url)
        res = self.waitLogin(self.browser)
        while res:
            res = self.waitLogin(self.browser)

    #   等待登录
    def waitLogin(self, browser):
        #   长等待获取是否获取用户名
        long_wait = WebDriverWait(browser, 30 * 1)
        try:
            long_wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.tips-wrap')))
            # (By.CSS_SELECTOR, '.header__logo')))  # 测试用
            cookies = browser.get_cookies()
            url_param = mytools.urlParam(browser.current_url)
            self.sig.getCookies.emit({
                'url': browser.current_url,
                'cookies': cookies,
                'appid': url_param['appid'],
                'dates': self.date_ary
            })
            browser.get("data:,")
        except BaseException:
            pass
        #   找寻无权限标识
        try:
            warning_no_permission = browser.find_element_by_css_selector(
                '.weui-desktop-msg.weui-desktop-msg_mini.weui-desktop-msg_temp-warn')
            if warning_no_permission:
                self.sig.getCookies.emit({})
        except BaseException:
            pass
        return True

    #   关闭
    def closeBrowser(self):
        if self.browser:
            self.browser.quit()

    #   浏览器初始化
    @staticmethod
    def browserInit():  # 实例化一个chrome浏览器
        chrome_options = webdriver.ChromeOptions()
        # options.add_argument(".\ChromePortable\App\Chrome\chrome.exe");
        chrome_options.binary_location = ".\\ChromePortable\\App\\Chrome\\chrome.exe"
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # browser = webdriver.Chrome(options=chrome_options)
        browser = webdriver.Chrome(options=chrome_options)
        # 设置等待超时
        return browser
