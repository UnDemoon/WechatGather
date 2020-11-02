'''
@Description: vivo数据采集类
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-07-01 11:36:41
'''
import requests
import time
import utils as mytools
import json


class GameweixinGather(object):
    def __init__(self, cookie: dict, dateAry: tuple):
        self.dateAry = dateAry
        startDate, endDate = dateAry
        self.colloct_conf = {
            'applist': {
                # 游戏列表
                'url': 'https://dev.vivo.com.cn/webapi/quickGame/listAll',
                'data': {
                    "timestamp": ''
                }
            },
            'user': {
                # 用户人数
                'url': 'https://dev.vivo.com.cn/webapi/data-service/graph',
                'data': {
                    'type': '3',
                    'dataId': '',
                    'nodeId': '46',
                    'startDate': startDate.toString('yyyy-MM-dd'),
                    'endDate': endDate.toString('yyyy-MM-dd'),
                    'timestamp': ''
                }
            },
            'remain': {
                # 留存
                'url': 'https://dev.vivo.com.cn/webapi/data-service/graph',
                'data': {
                    'type': '3',
                    'dataId': '',
                    'nodeId': '47',
                    'startDate': startDate.toString('yyyy-MM-dd'),
                    'endDate': endDate.toString('yyyy-MM-dd'),
                    'timestamp': ''
                }
            },
            'adv_applist': {
                #   广告部分app列表
                'url': 'https://adnet.vivo.com.cn/api/media/search',
                'data': {
                    'order': '',
                    'orderBy': '',
                    'status': '-1',     # 状态 全部
                    'appName': '',
                    'pageIndex': '1',
                    'pageSize': '20',
                    'platformType': '',
                    'timestamp': '',
                }
            },
            'adv_positionlist': {
                #   广告位列表
                'url': 'https://adnet.vivo.com.cn/api/position/search',
                'data': {
                    'order': 'desc',
                    'orderBy': 'updateDate',
                    'positionName': '',
                    'type': '-1',
                    'accessType': '2',
                    'status': '1',
                    'platformType': '',
                    'pageIndex': '1',
                    'pageSize': '20',
                    'mediaName': '',
                    'packageName': '',
                    'timestamp': '',
                }
            },
            'app_report': {
                #   应用报告
                'url': 'https://adnet.vivo.com.cn/api/report/getReportTableData',
                'data': {
                    'order': 'desc',            #
                    'orderBy': 'mediaId',          #
                    'startDate': '',            # 2020-7-24
                    'endDate': '',          # 2020-7-30
                    'dimensions': 'mediaId',           # mediaId
                    'platformType': '',         #
                    'positionType': '',         #
                    'metrics': 'view',          # view
                    'searchKeyWord': '',            #
                    'pageIndex': '1',            # 2
                    'pageSize': '20',         # 20
                    'timestamp': '',            # 1596163125367
                }
            },
            'position_report': {
                #   广告位报告
                'url': 'https://adnet.vivo.com.cn/api/report/getReportTableData',
                'data': {
                    'order': 'desc',            #
                    'orderBy': 'positionId',          #
                    'startDate': '',            # 2020-7-24
                    'endDate': '',          # 2020-7-30
                    'dimensions': 'positionId',           # mediaId
                    'platformType': '',         #
                    'positionType': '',         #
                    'metrics': 'view',          # view
                    'searchKeyWord': '',            #
                    'pageIndex': '1',            # 2
                    'pageSize': '20',         # 20
                    'timestamp': '',            # 1596163125367
                }
            },
        }
        #   配置requests session
        sess = requests.session()  # 新建session
        c = requests.cookies.RequestsCookieJar()        # 添加cookies到CookieJar
        for i in cookie:
            c.set(i["name"], i['value'])
            if i['name'] == 'oadstk':
                self.oadstk = i['value']
        sess.cookies.update(c)  # 更新session里cookies
        self.req = sess

    #   外部调用
    def runCollect(self):
        ur, re = self._base()    # 基础数据
        aal, apl, ar, pr = self._adv()     # 广告、收入数据
        return (ur, re, aal, apl, ar, pr)

    #   _get 方法
    def _get(self, url, para):
        res = self._subGet(url, para)
        while (res.get('code') != 0) and (res.get('code') != 1):
            mytools.randomSleep()
            res = self._subGet(url, para)
        return res

    #   _get子方法
    def _subGet(self, url, para):
        t = time.time()
        para['timestamp'] = str(int(round(t * 1000)))
        res = {}
        try:
            r = self.req.get(url, params=para)
            res = r.json()
        except BaseException as e:
            print(str(e))
        return res

    #   基础数据采集 用户、留存
    def _base(self):
        cf = self.colloct_conf
        users = []
        remain = []
        data = self._get(cf['applist']['url'], cf['applist']['data'])
        for app in data['data']:
            appid = app.get('id')
            # 获取用户相关数据
            para = cf['user']['data']
            para['dataId'] = appid
            res = self._get(cf['user']['url'], para)
            if len(res['data']['dataList']) > 0:
                users += list(map(lambda x: {
                                'appId': x['rpk_id'],
                                'day': x['effect_date'],
                                'new_user': x['new_user'],
                                'day_active_user': x['day_active_user'],
                                }, res['data']['dataList']))
            # 获取留存相关数据
            para = cf['remain']['data']
            para['dataId'] = app.get('id')
            res = self._get(cf['remain']['url'], para)
            if len(res['data']['dataList']) > 0:
                remain += list(map(lambda x: {
                                'appId': x['rpk_id'],
                                'day': x['effect_date'],
                                'next_day_left_rate': x['next_day_left_rate'],
                                'three_day_left_rate': x['three_day_left_rate'],
                                'seven_day_left_rate': x['seven_day_left_rate'],
                                }, res['data']['dataList']))
        return (users, remain)

    #   广告数据采集 收入、广告
    def _adv(self):
        cf = self.colloct_conf
        adv_app_list = self._multipage(
            cf['adv_applist']['url'], cf['adv_applist']['data'], 'medias',
            lambda x: {
                'appId': x['appId'],
                'appName': x['appName'],
                'mediaId': x['mediaId'],
            })
        adv_position_list = self._multipage(
            cf['adv_positionlist']['url'], cf['adv_positionlist']['data'], 'positions',
            lambda x: {
                'positionId': x['positionId'],
                'positionName': x['positionName'],
                'mediaId': x['mediaId'],
                'type': x['type'],
            })
        app_report = []
        position_report = []
        #   报告数据需要根据单日日期区间获取
        for day in mytools.dateList(self.dateAry):
            day = str(day)
            para = cf['app_report']['data']
            para['startDate'] = day
            para['endDate'] = day
            app_report += self._multipage(cf['app_report']['url'], para, 'dataList',
                                          lambda x: {
                                              **x,
                                              'day': day
                                          })  # 重构数据
            para = cf['position_report']['data']
            para['startDate'] = day
            para['endDate'] = day
            position_report += self._multipage(cf['position_report']['url'], para, 'dataList',
                                               lambda x: {
                                                   **x,
                                                   'day': day
                                               })  # 重构数据
        return (adv_app_list, adv_position_list, app_report, position_report)

    #   多页数据处理
    def _multipage(self, url: str, data: dict, data_key: str, filtr_fuc: object):
        res = []
        data['pageIndex'] = 1
        onepage = self._get(url, data)
        page_data = onepage['data'].get(data_key, [])
        while len(page_data) > 0:
            res += list(map(filtr_fuc, page_data))
            data['pageIndex'] = data['pageIndex'] + 1
            onepage = self._get(url, data)
            page_data = onepage['data'].get(data_key, [])
        return res
