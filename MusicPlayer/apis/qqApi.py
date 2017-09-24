# coding = utf-8

import json


from apiRequestsBase import HttpRequest, ignored


class QQApi(HttpRequest):

    default_timeout = 3.05

    def __init__(self):
        super(QQApi, self).__init__()

        self.headers['Host'] = 'c.y.qq.com'
        self.headers['Referer'] = 'https://y.qq.com/portal/playlist.html'

        self.playlistHeaders = self.headers.copy()
        self.playlistHeaders['Host'] = 'shc.y.qq.com'

        self.tokenHeaders = self.headers.copy()
        self.tokenHeaders['Host'] = 'base.music.qq.com'
        self.tokenHeaders.pop('Referer')

        self.token = self._get_qqtoken()
        self.key = self.token.get('key')
        self.sip = self.token.get('sip')[0]
        # 随便写一个就可以，原本是根据cookies里一个根据时间变化的参数确定的。
        self.guid = 3768717388
        if not self.sip:
            print('QQ 播放地址获取失败，请勿播放QQ音乐。')

    def httpRequest(self, *args, **kwargs):
        html = super(QQApi, self).httpRequest(*args, **kwargs)

        return html.text

    def _get_qqtoken(self):
        token_url = 'http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?' + \
            'json=3&guid=3768717388&g_tk=938407465&loginUin=0&hostUin=0&' + \
            'format=jsonp&inCharset=GB2312&outCharset=GB2312&notice=0&' + \
            'platform=yqq&jsonpCallback=jsonCallback&needNewCode=0'
        
        data = self.httpRequest(token_url, method='GET', headers=self.tokenHeaders)
        
        with ignored():
            data = data[len("jsonCallback("):-len(");")]

            return json.loads(data)
        return {'key': '1', 'sip': [False]}

    def playList(self, ein=29):
        """
        ein控制返回的歌单。
        29, 59, 89....
        """
        url = 'https://c.y.qq.com/splcloud/fcgi-bin/'+\
        'fcg_get_diss_by_tag.fcg?rnd=0.5136307078685405&g_tk=5381&'+\
        'jsonpCallback=getPlaylist&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8'+\
        '&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=10000000&'+\
        'sortId=5&sin=30&ein={0}'.format(ein)

        response = self.httpRequest(url, method='GET')

        with ignored():
            data = json.loads(response[len('getPlaylist('):-len(')')])
        
            return data['data']['list']
        
        return False

    def getPlaylist(self, ids):
        url = 'https://shc.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0'+\
        '&disstid={0}&format=jsonp&g_tk=5381&jsonpCallback=playlistinfoCallback&loginUin=0&hostUin=0&'.format(ids)+\
        'format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
        
        response = self.httpRequest(url, method='GET', headers=self.playlistHeaders)
        
        # with ignored():
        data = json.loads(response[len('playlistinfoCallback('):-len(')')])
        data = data['cdlist'][0]

        newDatas = {}
        newDatas['trackCount'] = data['total_song_num']
        newDatas['name'] = data['dissname']
        newDatas['creator'] = {'nickname': data['nick']}
        newDatas['description'] = data['desc']
        songs = data['songlist']

        imgUrl = 'https://y.gtimg.cn/music/photo_new/'

        for i in songs:
            i['name'] = i['songname']
            i['artists'] = [{'name': ';'.join([x['name'] for x in i['singer']])}]
            i['duration'] = int(i['interval']) * 1000
            i['album'] = {'blurPicUrl': imgUrl + 'T002R300x300M000' + i['albummid'] + '.jpg'}
            i['mp3Url'] = '{0}C400{1}.m4a?vkey={2}&guid={3}'.format(self.sip, i['songmid'], self.key, self.guid)

        newDatas['tracks'] = songs

        return newDatas

        return False


qqApi = QQApi()


if __name__ == '__main__':
    # a = qqApi.playList(29)
    # http://dl.stream.qqmusic.qq.com/
    # C400 0000HZ4N01bJ8a.m4a
    #           0000HZ4N01bJ8a
    # ?vkey=42BBA28D626228E8C360FEFE03817E3A15885426F969484963ABFBC4D197A5CEF4E3ED7911F3236150212564FA9F2F1B0AD02AF37FF181A2&guid=3768717388&uin=0&fromtag=66
    # ?vkey=1B6C73D1685155EBB75D36995A81FD2DEFEA2BA30389B99675EDDB367BF4FFCFC075B63FBFFA9F4642A411C02A248FEF24E91379DBDEBA7D&guid=780782017&uin=0&fromtag=66
    # a = qqApi._get_qqtoken()
    # print(qqApi.key, qqApi.sip)    
    a = qqApi.getPlaylist(3581667044)
    for i in a['tracks']:
        print(i)
        # print(i['dissname'])
        # print(i['dissid'])

    # for i in a:
        # print(i)
    #     print(a[i])