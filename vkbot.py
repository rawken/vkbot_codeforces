import vk
import json
from datetime import datetime   
import requests
import time
import locale
import pytz
import collections
from pytz import timezone
from pytz import utc

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
accesstoken = ''
group_id = 
session = vk.Session(access_token=accesstoken)
api = vk.API(session)
i = 0
with open('contest_ids.json', 'r') as conid:
    a = json.loads(conid.read())

def short_tnd_url(i):
    req_ref = reqres['result'][i]['startTimeSeconds']
    dt = utc.localize(datetime.utcfromtimestamp(req_ref))
    dt = dt.astimezone(timezone('Europe/Moscow'))
    params = collections.OrderedDict()
    params['day'] = int(dt.strftime('%d'))
    params['month'] = int(dt.strftime('%m'))
    params['year'] = dt.strftime('%Y')
    params['hour'] = dt.strftime('%H')
    params['min'] = dt.strftime('%M')
    params['sec'] = int(dt.strftime('%S'))
    params['p1'] = 166
    tnd_req = requests.get('https://www.timeanddate.com/worldclock/fixedtime.html?', params)
    key = ''
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key='+key
    payload = {'longUrl': tnd_req.url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data = json.dumps(payload), headers = headers).text
    r = json.loads(r)
    return r['id']

def format_post(post, i):
    name = str(reqres['result'][i]['name'])
    if 'Educational' in (reqres['result'][i]['name']):
        name_emoji = '&#127891;'
    else:
        name_emoji = '&#128161;'
    dur_hours = reqres['result'][i]['durationSeconds'] // 3600
    dur_minutes = reqres['result'][i]['durationSeconds'] % 3600 // 60
    if dur_minutes == 0:
        duration = str(dur_hours) + ':00'
    else:
        duration = str(dur_hours) + ':' + str(dur_minutes)
    start_time_sec = int(reqres['result'][i]['startTimeSeconds'])
    end_time_sec = int(start_time_sec + reqres['result'][i]['durationSeconds'])
    start_dt = utc.localize(datetime.utcfromtimestamp(start_time_sec))
    start_dt = start_dt.astimezone(timezone('Europe/Moscow'))
    end_dt = utc.localize(datetime.utcfromtimestamp(end_time_sec))
    end_dt = end_dt.astimezone(timezone('Europe/Moscow'))
    contest_id = str(reqres['result'][i]['id'])
    start_date = str(start_dt.strftime('%d.%m.%Y (%a) %H:%M'))
    end_time = str(end_dt.strftime('%H:%M')) + ' (МСК)'
    post = [name_emoji + name,
    '\n',
    '\n',
    '&#9203;' + 'Длительность - ' + duration,
    '\n',
    '&#128197;' + 'Время контеста - ' + start_date + '-' + end_time,
    '\n',
    '&#9888;' + 'Начало в вашем регионе - ' + str(short_url)]
    return post

while True:
    req = requests.get('http://codeforces.com/api/contest.list?')
    req = req.text
    reqres = json.loads(req)
    phase = reqres['result'][i]['phase']
    contest_id = reqres['result'][i]['id']
    relativeTime = reqres['result'][i]['relativeTimeSeconds']
    contest_url = 'http://codeforces.com/contests/' + str(contest_id)
    short_url = short_tnd_url(i)
    if phase == 'BEFORE' and relativeTime >= -172800 and contest_id not in a: 
        a.append(reqres['result'][i]['id'])
        post = 0
        post = format_post(post, i)
        post  = ' '.join(post)
        api.wall.post(
            owner_id = group_id, 
            from_group = 1, 
            message = post,
            attachments = contest_url
        )
        with open('contest_ids.json', 'a') as conid:
            json.dump(contest_id, conid)
        i += 1
    else:
        i = 0
    time.sleep(60)
