# -*- coding: utf-8 -*-

import os
import sys, getopt

import urllib
import hashlib
import requests
import re
import json
import time

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
}

USAGE = '''

    Usage:

        tiktok-crawler http://v.douyin.com/8YVQBV/ all 200

        tiktok-crawler http://v.douyin.com/82UayF/ latest 20

'''

FETCH_LATEST = 'latest'
FETCH_ALL = 'all'
SLEEP_TIME = 1

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

    def __init__(self, url, type, max):
        self.url = get_real_address(url)
        self.type = type
        self.max = max

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
            return { 'count': 0, 'list': [] }

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

        max_cursor, videos, page = None, { 'count': 0, 'list': [] }, 1

        while True:

            if max_cursor:
                user_video_params['max_cursor'] = str(max_cursor)

            res = requests.get(user_video_url, headers=HEADERS, params=user_video_params)
            try:
                contentJson = json.loads(res.content.decode('utf-8'))
            except:
                # fetch exception, try again
                continue

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

            if len(aweme_list) > 0:
                page += 1

            time.sleep(SLEEP_TIME)

            if self.type == FETCH_LATEST and len(aweme_list) > 0:
                break

            if videos['count'] >= self.max:
                break

        return videos

    def fetch_user_videos(self):
        number = re.findall(r'share/user/(\d+)', self.url)
        if not len(number): return
        dytk = get_dytk(self.url)
        if not dytk: return
        user_id = number[0]
        videos = self._fetch_user_media(user_id, dytk, self.url)
        sys.stdout.write(str(videos).replace("'", '"'))

    def _fetch_challenge_media(self, challenge_id, url):

        if not challenge_id:
            return { 'count': 0, 'list': [] }

        hostname = urllib.parse.urlparse(url).hostname
        signature = self.generateSignature(str(challenge_id) + '9' + '0')
        challenge_video_url = "https://%s/aweme/v1/challenge/aweme/" % hostname
        challenge_video_params = {
            'ch_id': str(challenge_id),
            'count': '9',
            'cursor': '0',
            'aid': '1128',
            'screen_limit': '3',
            'download_click_limit': '0',
            '_signature': signature
        }

        cursor, videos, page = None, { 'count': 0, 'list': [] }, 1

        while True:

            if cursor:
                challenge_video_params['cursor'] = str(cursor)
                challenge_video_params['_signature'] = self.generateSignature(str(challenge_id) + '9' + str(cursor))

            res = requests.get(challenge_video_url, headers=HEADERS,params=challenge_video_params)
            try:
                contentJson = json.loads(res.content.decode('utf-8'))
            except:
                # fetch exception, try again
                continue

            aweme_list = contentJson.get('aweme_list', [])

            if not aweme_list:
                break
            for aweme in aweme_list:
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
                    'desc': '',
                    'video_url': video_url,
                    'image_url': image_url,
                    'like': 0,
                    'share': 0,
                })
                videos['count'] += 1
            if contentJson.get('has_more'):
                cursor = contentJson.get('cursor')
            else:
                break

            page += 1

            time.sleep(SLEEP_TIME)

            if self.type == FETCH_LATEST:
                break

            if videos['count'] >= self.max:
                break

        return videos

    def fetch_challenge_videos(self):
        challenge = re.findall('share/challenge/(\d+)', self.url)
        if not len(challenge): return
        challenges_id = challenge[0]
        videos = self._fetch_challenge_media(challenges_id, self.url)
        sys.stdout.write(str(videos).replace("'", '"'))

    def fetch(self):
        if re.search('share/user', self.url):
            self.fetch_user_videos()
        elif re.search('share/challenge', self.url):
            self.fetch_challenge_videos()
        else:
            usage()

def usage():
    print(USAGE)

def run():
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)

    fetch_url = sys.argv[1]
    fetch_type = sys.argv[2]
    if fetch_type != FETCH_LATEST and fetch_type != FETCH_ALL:
        usage()
        sys.exit(1)
    try:
        fetch_max = int(sys.argv[3])
    except:
        usage()
        sys.exit(1)

    crawler = TikTokCrawler(fetch_url, fetch_type, fetch_max)

    crawler.fetch()

if __name__ == "__main__":

    run()
