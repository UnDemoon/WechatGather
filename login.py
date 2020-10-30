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
import time


# 登录
def oppo_lg(browser: object, url: str, username: str, password: str, wait: object):
    browser.set_page_load_timeout(8)
    try:
        browser.get(url)
    except BaseException:
        # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
        browser.execute_script("window.stop()")
    #   切换密码登录
    switch_lable = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.tabloginway div:last-of-type')))
    switch_lable.click()
    # 获取用户名输入框
    user = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.index_content input[type="text"]')))
    # 获取密码输入框
    passwd = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.password [type="password"]')))
    # 输入用户名
    user.send_keys(username)
    # 输入密码
    passwd.send_keys(password)
    #   点击登录
    loginbtn = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.passlogin>button')))
    loginbtn.click()
    #   长等待获取是否获取用户名
    long_wait = WebDriverWait(browser, 60)
    login_flag = False
    try:
        login_flag = login_flag or long_wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[class~="userInfo_name"]')))
    except BaseException:
        pass
    if login_flag:
        cookies = browser.get_cookies()
        return cookies
    else:
        return False


def oppo_jump(browser: object, url: str, username: str, password: str, wait: object):
    browser.set_page_load_timeout(5)
    try:
        browser.get(url)
    except BaseException:
        # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
        browser.execute_script("window.stop()")
    browser.get("https://u.oppomobile.com/main/index.html")
    time.sleep(3)
    cookies = browser.get_cookies()
    return cookies


# vivo login
def vivo_lg(browser: object, url: str, username: str, password: str, wait: object):
    browser.set_page_load_timeout(8)
    try:
        browser.get(url)
    except BaseException:
        # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
        browser.execute_script("window.stop()")
    # 获取用户名输入框
    user = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#frm-login input[name="name"]')))
    # 获取密码输入框
    passwd = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#frm-login [name="password"]')))
    # 输入用户名
    user.send_keys(username)
    # 输入密码
    passwd.send_keys(password)

    #   等待用户输入验证码

    #   长等待获取是否获取用户名
    long_wait = WebDriverWait(browser, 120)
    login_flag = False
    try:
        login_flag = login_flag or long_wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#yetLogin .userName')))
    except BaseException:
        pass
    if login_flag:
        cookies = browser.get_cookies()
        return cookies
    else:
        return False


# 头条 login
def toutiao_lg(browser: object, url: str, username: str, password: str, wait: object):
    browser.set_page_load_timeout(8)
    try:
        browser.get(url)
    except BaseException:
        # 当页面加载时间超过设定时间，通过js来stop，即可执行后续动作
        browser.execute_script("window.stop()")
    #   打开密码输入
    login_btn = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.enter-button')))
    login_btn.click()
    #   表单填充   visibility_of_element_located 可见时才触发
    user = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.ivu-modal-wrap input[type=text]')))
    passwd = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.ivu-modal-wrap input[type=password]')))
    user.send_keys(username)
    passwd.send_keys(password)
    #   checkbox 允许协议
    check = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.ivu-modal-wrap .ivu-checkbox-wrapper')))
    check.click()
    #   点击登录
    loginbtn = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.single-btn>button')))
    loginbtn.click()
    #   长等待获取是否获取用户名
    long_wait = WebDriverWait(browser, 60)
    login_flag = False
    try:
        mksure = long_wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.ivu-modal-confirm-footer button')))   # logout元素是否存在，存在说明已登录
        mksure.click()
    except BaseException:
        pass
    try:
        login_flag = login_flag or long_wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[class~="logout-dropdown"]')))   # logout元素是否存在，存在说明已登录
    except BaseException:
        pass
    if login_flag:
        cookies = browser.get_cookies()
        return cookies
    else:
        return False
