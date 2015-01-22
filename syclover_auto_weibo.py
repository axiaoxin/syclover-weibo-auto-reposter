# !/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import os
import time
import requests
import logging
import threading
from collections import OrderedDict

BASE_DIR = os.path.realpath(os.path.dirname(__file__))

SESSION = requests.session()
SESSION.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))

LOG_FORMAT = '<%(levelname)s> %(asctime)s: %(message)s'
logging.basicConfig(filename=os.path.join(BASE_DIR, '.syclover-auto-weibo.log'),
                    level=logging.INFO,
                    format=LOG_FORMAT)

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
ACCOUNT = os.getenv('ACCOUNT')
PASSWORD = os.getenv('PASSWORD')

REPOST_URL = 'https://api.weibo.com/2/statuses/repost.json'
REPOST_PHRASE = '转一个'

with open(os.path.join(BASE_DIR, 'syclovers')) as f:
    SYCLOVERS = [uid.strip() for uid in f]


def is_syclover(uid):
    return str(uid) in SYCLOVERS


def load_reposted_id(id_type):
    if id_type == 'atme_since_id':
        with open(os.path.join(BASE_DIR, '.atme_since_id')) as f:
            return int(f.read().decode('utf-8') or 0)
    elif id_type == 'comment_since_id':
        with open(os.path.join(BASE_DIR, '.comment_since_id')) as f:
            return int(f.read().decode('utf-8') or 0)


def save_reposted_id(id_type, since_id):
    if id_type == 'atme_since_id':
        with open(os.path.join(BASE_DIR, '.atme_since_id'), 'w') as f:
            f.write(str(since_id).encode('utf-8'))
    elif id_type == 'comment_since_id':
        with open(os.path.join(BASE_DIR, '.comment_since_id'), 'w') as f:
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
    r = SESSION.post(url, data=post_data, headers=headers)
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
    r = SESSION.post(url, data=post_data)
    data = r.json()
    return data


def repost(params):
    resp = SESSION.post(REPOST_URL, data=params)
    try:
        resp.raise_for_status()
    except Exception as e:
        logging.debug(str(e))


def check_atme(delay=3):
    statuses_mentions_url = 'https://api.weibo.com/2/statuses/mentions.json'
    data = get_token()
    access_token = data['access_token']
    since_id = load_reposted_id('atme_since_id')
    logging.info('[@ in status] since_id: %s' % since_id)
    params = {
        'source': APP_KEY,
        'access_token': access_token,
        'since_id': since_id
    }
    r = SESSION.get(statuses_mentions_url, params=params)
    statuses = r.json()['statuses']
    if statuses:
        for status in statuses:
            if not is_syclover(status['user']['id']):
                continue
            if REPOST_PHRASE not in status['text']:
                continue
            params = {
                'source': APP_KEY,
                'access_token': access_token,
                'is_comment': 3,
                'id': status['id'],
            }

            logging.info('[REPOST] @ in status, status_id: %s, uid: %s' %
                         (status['id'], status['user']['id']))
            time.sleep(delay)
            threading.Thread(target=repost, args=(params,)).start()
        save_reposted_id('atme_since_id', statuses[0]['id'])
        logging.info('[@ in status] new_since_id: %s' % statuses[0]['id'])


def check_comment(delay=3):
    comments_to_me_url = 'https://api.weibo.com/2/comments/to_me.json'
    since_id = load_reposted_id('comment_since_id')
    logging.info('[@ in comment] since_id:%s' % since_id)
    data = get_token()
    params = {
        'source': APP_KEY,
        'access_token': data['access_token'],
        'since_id': since_id
    }
    r = SESSION.get(comments_to_me_url, params=params)
    comments = r.json()['comments']

    if not comments:
        comments_mentions_url = 'https://api.weibo.com/2/comments/mentions.json'
        r = SESSION.get(comments_mentions_url, params=params)
        comments = r.json()['comments']

    results = OrderedDict()
    for a_comment in comments:
        results[a_comment['id']] = {
            'text': a_comment['text'],
            'wid': a_comment['status']['id'],
            'weibo': a_comment['status']['text'],
            'uid': a_comment['user']['id'],
        }

    if results:
        for _, value_dict in results.iteritems():
            if not is_syclover(value_dict['uid']):
                continue
            if REPOST_PHRASE not in value_dict['text']:
                continue
            params = {
                'source': APP_KEY,
                'access_token': data['access_token'],
                'id': value_dict['wid'],
                'is_comment': 3,
                # 'status': 'Repost!'
            }
            time.sleep(delay)
            threading.Thread(target=repost, args=(params,)).start()
            logging.info('[REPOST] @ in comment, status_id: %s, uid: %s' %
                         (value_dict['wid'], value_dict['uid']))

        save_reposted_id('comment_since_id', results.keys()[0])
        logging.info('[@ in comment] new_since_id: %s' % results.keys()[0])

if __name__ == '__main__':
    check_atme()
    check_comment()
    logging.info('=' * 48)
