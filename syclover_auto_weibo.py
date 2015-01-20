# !/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import os
import redis
import requests
import logging
import threading

LOG_FORMAT = '<%(levelname)s> %(asctime)s: %(message)s'
logging.basicConfig(filename='syclover-auto-weibo.log',
                    level=logging.DEBUG,
                    format=LOG_FORMAT)

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
ACCOUNT = os.getenv('ACCOUNT')
PASSWORD = os.getenv('PASSWORD')

REPOST_URL = 'https://api.weibo.com/2/statuses/repost.json'

REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = os.getenv('REDIS_PORT') or 6379

REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def auth():
    url = "https://api.weibo.com/oauth2/authorize"
    auth_url = "%s?client_id=%s&redirect_uri=%s" % (url, APP_KEY, REDIRECT_URI)
    post_data = {
        'client_id': APP_KEY,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'action': 'submit',
        'userId': ACCOUNT,
        'passwd': PASSWORD,
        'isLoginSina': 0,
        'from': '',
        'regCallback': '',
        'state': '',
        'ticket': '',
        'withOfficalFlag': 0
    }
    headers = {
        'Referer': auth_url,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(url, data=post_data, headers=headers)
    code = r.url.split('=')[1]
    return code


def get_token():
    code = auth()
    url = "https://api.weibo.com/oauth2/access_token"
    post_data = {
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    r = requests.post(url, data=post_data)
    data = r.json()
    return data


def repost(params):
    requests.post(REPOST_URL, data=params)


def check_atme():
    statuses_mentions_url = 'https://api.weibo.com/2/statuses/mentions.json'
    data = get_token()
    access_token = data['access_token']
    params = {
        'source': APP_KEY,
        'access_token': access_token,
        'filter_by_type': 0,
    }
    r = requests.get(statuses_mentions_url, params=params)
    data = r.json()['statuses']
    if data:
        data = data[0]
        text = data['text']
        text_id = data['id']
        replied_id = REDIS.get('replied_id')
        logging.info('[status at] text_id:%s text:%s replied_id:%s' % (text_id, text, replied_id))
        if not replied_id:
            REDIS.set('replied_id', text_id)
        if text_id != replied_id:
            params = {
                'source': APP_KEY,
                'access_token': access_token,
                'is_comment': 3,
                'id': text_id,
            }

            threading.Thread(target=repost, args=(params,)).start()
            REDIS.set('replied_id', text_id)


def check_comment():
    comments_to_me_url = 'https://api.weibo.com/2/comments/to_me.json'
    since_id = REDIS.get('since_id')
    if not since_id:
        REDIS.set('since_id', 0)
        since_id = 0
    data = get_token()
    params = {
        'source': APP_KEY,
        'access_token': data['access_token'],
        'since_id': since_id
    }
    r = requests.get(comments_to_me_url, params=params)
    comments = r.json()['comments']

    if not comments:
        comments_mentions_url = 'https://api.weibo.com/2/comments/mentions.json'
        r = requests.get(comments_mentions_url, params=params)
        comments = r.json()['comments']

    results = {}
    for a_comment in comments:
        results[a_comment['id']] = {
            'text': a_comment['text'],
            'wid': a_comment['status']['id'],
            'weibo': a_comment['status']['text'],
        }
    results = sorted(results.iteritems(),
                     key=lambda d: d[0],
                     reverse=True)

    if results:
        logging.info('[comment at] since_id:%s new_since_id:%s' % (since_id, results[0][0]))
        for i in results:
            params = {
                'source': APP_KEY,
                'access_token': data['access_token'],
                'id': i[1]['wid'],
                'is_comment': 3,
                'status': 'hhh'
            }
            threading.Thread(target=repost, args=(params,)).start()

        REDIS.set('since_id', results[0][0])

if __name__ == '__main__':
    #check_atme()
    check_comment()
