'''
@Description: 数据采集类
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-07-01 11:36:41
'''
import json
import requests
import time
# import urllib
import utils as mytools


class GameweixinGather(object):
    def __init__(self, appid: str, cookie: dict, dateAry: tuple):
        super(GameweixinGather, self).__init__()
        self.dateAry = dateAry
        self.appid = appid
        self.colloct_conf = {
            #   渠道列表接口
            "perm_list": {
                "url":
                "https://game.weixin.qq.com/cgi-bin/gamewxagchannelwap/getsharepermuserinfo",
                "params": {
                    "appid": self.appid,
                    "needLogin": "true",
                    "method": "GET",
                    "abtest_cookie": "",
                    "abt": "",
                    "build_version": "2020090717",
                    "QB": ""
                }
            },
            #    渠道数据
            "channel_share_data": {
                "url":
                "https://game.weixin.qq.com/cgi-bin/gamewxagchannelwap/getwxagstatcustomchannelsharedata",
                "params": {
                    "data": "",
                    "needLogin": "true",
                    "method": "GET",
                    "abtest_cookie": "",
                    "abt": "",
                    "build_version": "2020090717",
                    "QB": ""
                }
            }
        }
        hd = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "referer": "https://game.weixin.qq.com/cgi-bin/minigame/static/channel_side/index.html?appid=" + self.appid,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4302.0 Safari/537.36"
        }
        self.req = self._setSession(cookie, hd)

    #   run方法重写 start调用
    def startRun(self):
        res_list = []
        channel_list = self._permList()
        staruix, enduix = mytools.dateToStamps(self.dateAry)
        duration_seconds = enduix - staruix
        for item in channel_list:
            param_data = {
                    "need_app_info": True,
                    "appid": self.appid,
                    "sequence_index_list": [
                        {
                            "size_type": 24,
                            "stat_type": 1000088,
                            "data_field_id": 6,
                            "time_period": {
                                "start_time": staruix,
                                "duration_seconds": duration_seconds
                            },
                            "filter_list": [
                                {
                                    "name": item.get("channel_name"),
                                    "field_id": 5,
                                    "value": item.get("out_channel_id"),
                                },
                                {
                                    "field_id": 4,
                                    "value": item.get("out_group_id"),
                                }
                            ],
                            "requestType": "sequence"
                        },
                        {
                            "size_type": 24,
                            "stat_type": 1000088,
                            "data_field_id": 6,
                            "time_period": {
                                "start_time": staruix,
                                "duration_seconds": duration_seconds
                            },
                            "requestType": "sequence",
                            "filter_list": [
                                {
                                    "name": item.get("channel_name"),
                                    "field_id": 5,
                                    "value": item.get("out_channel_id"),
                                },
                                {
                                    "field_id": 4,
                                    "value": item.get("out_group_id"),
                                }
                            ]
                        }
                    ],
                    "group_index_list": [],
                    "rank_index_list": [],
                    "table_index_list": [],
                    "version": 0
                }
            temp = self._channelData(param_data, item)
            res_list += temp
            mytools.randomSleep()
        return res_list

    #   设置session
    def _setSession(self, ck: dict, hd: dict):
        #   配置requests session
        sess = requests.session()  # 新建session
        c = requests.cookies.RequestsCookieJar()  # 添加cookies到CookieJar
        for i in ck:
            c.set(i["name"], i['value'])
        sess.cookies.update(c)  # 更新session里cookies
        sess.headers.update(hd)  # 更新session里cookies
        return sess

    #   _get 方法
    def _get(self, url, para):
        res = self._subGet(url, para)
        while res.get('errcode') != 0:
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
            # mytools.logFile(str(r.text))
            res = r.json()
        except BaseException as e:
            print(str(e))
        return res

    # 获取下拉列表
    def _permList(self):
        conf = self.colloct_conf['perm_list']
        res = self._get(conf['url'], conf['params'])
        # mytools.logFile(json.dumps(res))
        res = res['data']['share_perm_data']['perm_list']
        return res

    # 获取活跃数据
    def _channelData(self, param_data: dict, info: dict):
        conf = self.colloct_conf['channel_share_data']
        param = conf['params']
        param['data'] = json.dumps(param_data)
        # print(param)
        res = self._get(conf['url'], param)
        # mytools.logFile(json.dumps(res))
        res = res['data']['sequence_data_list'][0]['point_list']
        res = map(lambda x: {
            'day': x['label'],
            'active_user': x.get('value', 0),
            'adv_appid': self.appid,
            'out_group_id': info.get('out_group_id'),
            'out_channel_id': info.get('out_channel_id'),
            'channel_name': info.get('channel_name'),
            }, res)
        return res
