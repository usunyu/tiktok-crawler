# -*- coding: utf-8 -*-

import os
import sys, getopt

import urllib.parse
import hashlib
import requests
import re
import json

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
}

def get_real_address(url):
    if url.find('v.douyin.com') < 0: return url
    res = requests.get(url, headers=HEADERS, allow_redirects=False)
    return res.headers['Location']

def get_dytk(url):
    res = requests.get(url, headers=HEADERS)
    if not res: return None
    dytk = re.findall("dytk: '(.*)'", res.content.decode('utf-8'))
    if len(dytk): return dytk[0]
    return None

class TikTokCrawler(object):

    def __init__(self, url):
        self.url = get_real_address(url)

    @staticmethod
    def generateSignature(value):
        p = os.popen('node fuck-byted-acrawler.js %s' % value)
        return p.readlines()[0]

    @staticmethod
    def calculateFileMd5(filename):
        hmd5 = hashlib.md5()
        fp = open(filename, "rb")
        hmd5.update(fp.read())
        return hmd5.hexdigest()

    def _fetch_user_media(self, user_id, dytk, url):
        if not user_id:
            print("Number %s does not exist" % user_id)
            return
        hostname = urllib.parse.urlparse(url).hostname
        signature = self.generateSignature(str(user_id))
        user_video_url = "https://%s/aweme/v1/aweme/post/" % hostname
        user_video_params = {
            'user_id': str(user_id),
            'count': '21',
            'max_cursor': '0',
            'aid': '1128',
            '_signature': signature,
            'dytk': dytk
        }
        max_cursor, videos = None, { 'count': 0, 'list': [] }
        while True:
            if max_cursor:
                user_video_params['max_cursor'] = str(max_cursor)
            res = requests.get(user_video_url, headers=HEADERS, params=user_video_params)
            contentJson = json.loads(res.content.decode('utf-8'))
            aweme_list = contentJson.get('aweme_list', [])
            for aweme in aweme_list:
                share_info = aweme.get('share_info', {})
                statistics = aweme.get('statistics', {})
                video = aweme.get('video', {})
                play_addr = video.get('play_addr', {})
                video_list = play_addr.get('url_list', [])
                cover = video.get('cover', {})
                cover_list = cover.get('url_list', [])
                video_url, image_url = '', ''
                if len(video_list) > 0:
                    video_url = video_list[0]
                if len(cover_list) > 0:
                    image_url = cover_list[0]
                videos['list'].append({
                    'desc': share_info.get('share_desc', ''),
                    'video_url': video_url,
                    'image_url': image_url,
                    'like': statistics.get('digg_count', 0),
                    'share': statistics.get('forward_count', 0),
                })
                videos['count'] += 1
            if contentJson.get('has_more'):
                max_cursor = contentJson.get('max_cursor')
            else:
                break

        if videos['count'] == 0:
            print("There's no video in number %s." % user_id)

        return videos

    def fetch_user_videos(self):
        number = re.findall(r'share/user/(\d+)', self.url)
        if not len(number): return
        dytk = get_dytk(self.url)
        if not dytk: return
        user_id = number[0]
        videos = self._fetch_user_media(user_id, dytk, self.url)
        sys.stdout.write(str(videos).replace("'", '"'))
        sys.stdout.write('\n')

    def fetch(self):
        if re.search('share/user', self.url):
            self.fetch_user_videos()
        elif re.search('share/challenge', self.url):
            pass
        else:
            usage()

def usage():
    print('''
          Usage:

          python tiktok-crawler.py http://v.douyin.com/8YVQBV/
          ''')

if __name__ == "__main__":

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    fetch_url = sys.argv[1]
    crawler = TikTokCrawler(fetch_url)
    crawler.fetch()
