# !/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import os
import time
import requests
import logging
import threading

LOG_FORMAT = '<%(levelname)s> %(asctime)s: %(message)s'
logging.basicConfig(filename='syclover-auto-weibo.log',
                    level=logging.INFO,
                    format=LOG_FORMAT)

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
ACCOUNT = os.getenv('ACCOUNT')
PASSWORD = os.getenv('PASSWORD')

REPOST_URL = 'https://api.weibo.com/2/statuses/repost.json'

def load_reposted_id(id_type):
    if id_type == 'atme_since_id':
        with open('./.atme_since_id') as f:
            return int(f.read().decode('utf-8') or 0)
    elif id_type == 'comment_since_id':
        with open('./.comment_since_id') as f:
            return int(f.read().decode('utf-8') or 0)

def save_reposted_id(id_type, since_id):
    if id_type == 'atme_since_id':
        with open('./.atme_since_id', 'w') as f:
            f.write(str(since_id).encode('utf-8'))
    elif id_type == 'comment_since_id':
        with open('./.comment_since_id', 'w') as f:
            f.write(str(since_id).encode('utf-8'))


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


def repost(params, delay=3):
    time.sleep(delay)
    requests.post(REPOST_URL, data=params)


def check_atme():
    statuses_mentions_url = 'https://api.weibo.com/2/statuses/mentions/ids.json'
    data = get_token()
    access_token = data['access_token']
    since_id = load_reposted_id('atme_since_id')
    logging.info('[@ in status] since_id: %s' % since_id)
    params = {
        'source': APP_KEY,
        'access_token': access_token,
        'since_id': since_id
    }
    r = requests.get(statuses_mentions_url, params=params)
    mentions_ids = r.json()['statuses']
    if mentions_ids:
        for text_id in mentions_ids:
            params = {
                'source': APP_KEY,
                'access_token': access_token,
                'is_comment': 3,
                'id': text_id,
            }

            logging.info('[REPOST] @ in status, status_id: %s' % text_id)
            threading.Thread(target=repost, args=(params,)).start()
        save_reposted_id('atme_since_id', mentions_ids[0])
        logging.info('[@ in status] new_since_id: %s' % mentions_ids[0])


def check_comment():
    comments_to_me_url = 'https://api.weibo.com/2/comments/to_me.json'
    since_id = load_reposted_id('comment_since_id')
    logging.info('[@ in comment] since_id:%s' % since_id)
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
        for i in results:
            params = {
                'source': APP_KEY,
                'access_token': data['access_token'],
                'id': i[1]['wid'],
                'is_comment': 3,
                # 'status': 'Repost!'
            }
            threading.Thread(target=repost, args=(params,)).start()
            logging.info('[REPOST] @ in comment, status_id: %s' % i[1]['wid'])

        save_reposted_id('comment_since_id', results[0][0])
        logging.info('[@ in comment] new_since_id: %s' % results[0][0])

if __name__ == '__main__':
    check_atme()
    check_comment()
    logging.debug('=' * 48)
