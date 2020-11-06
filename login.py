'''
@Description: 
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-06-09 12:04:41
'''
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import utils as myTools
from PyQt5.Qt import QThread
from selenium import webdriver


class MyBrowser(QThread):
    def __init__(self, sigGetCookies: object, date_ary: tuple):
        super().__init__()
        self.sig = sigGetCookies
        self.date_ary = date_ary

    #   run
    def run(self):
        browser = self.browserInit()
        res = self.waitLogin(browser)
        while res:
            res = self.waitLogin(browser)

    #   等待登录
    def waitLogin(self, browser):
        #   长等待获取是否获取用户名
        long_wait = WebDriverWait(browser, 60 * 1)
        login_flag = False
        try:
            print(1)
            login_flag = login_flag or long_wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.header__logo')))
            cookies = browser.get_cookies()
            url_param = myTools.urlParam(browser.current_url)
            self.sig.getCookies.emit({
                'cookies': cookies,
                'appid': url_param['appid'],
                'dates': self.date_ary
            })
            browser.get("data:,")
        except BaseException:
            pass
        return True

    #   浏览器初始化
    def browserInit(self):      # 实例化一个chrome浏览器
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
