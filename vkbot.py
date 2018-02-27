import json
from datetime import datetime   
import requests
import time
import locale
import collections

import pytz
import vk
from pytz import timezone
from pytz import utc


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
accesstoken = ''
session = vk.Session(access_token=accesstoken)
api = vk.API(session)
GROUP_ID = ''
START_ID = 0
GKEY = ''
TIMEZONE = timezone('Europe/Moscow')


def short_tnd_url(i):
    req_ref = reqres['result'][i]['startTimeSeconds']
    dt = utc.localize(datetime.utcfromtimestamp(req_ref))
    dt = dt.astimezone(TIMEZONE)
    params = collections.OrderedDict()
    params['day'] = int(dt.strftime('%d'))
    params['month'] = int(dt.strftime('%m'))
    params['year'] = dt.strftime('%Y')
    params['hour'] = dt.strftime('%H')
    params['min'] = dt.strftime('%M')
    params['sec'] = int(dt.strftime('%S'))
    params['p1'] = 166
    tnd_req = requests.get('https://www.timeanddate.com/worldclock/fixedtime.html?', params)
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(GKEY)
    payload = {'longUrl': tnd_req.url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers).text
    r = json.loads(r)
    return r['id']


def format_post(i):
    name = str(reqres['result'][i]['name'])
    if reqres['result'][i]['startTimeSeconds'] == reqres['result'][i+1]['startTimeSeconds']:
        name = name.replace(')', ', Div.2)')
    
    if 'Educational' in (reqres['result'][i]['name']):
        name_emoji = '&#127891;'        #'&#127891;' is graduation cap emoji
    else:
        name_emoji = '&#128161;'        #'&#128161;' is electric light bulb emoji
    
    dur_hours = reqres['result'][i]['durationSeconds'] // 3600
    dur_minutes = reqres['result'][i]['durationSeconds'] % 3600 // 60
    
    if dur_minutes == 0:
        duration = '{}:00'.format(str(dur_hours))
    else:
        duration = '{}:{}'.format(str(dur_hours), str(dur_minutes))

    start_time_sec = int(reqres['result'][i]['startTimeSeconds'])
    end_time_sec = int(start_time_sec + reqres['result'][i]['durationSeconds'])
    
    start_dt = utc.localize(datetime.utcfromtimestamp(start_time_sec))
    start_dt = start_dt.astimezone(TIMEZONE)
    
    end_dt = utc.localize(datetime.utcfromtimestamp(end_time_sec))
    end_dt = end_dt.astimezone(TIMEZONE)
    
    contest_id = str(reqres['result'][i]['id'])
    start_date = str(start_dt.strftime('%d.%m.%Y (%a) %H:%M'))
    end_time = '{} (МСК)'.format(str(end_dt.strftime('%H:%M')))

    post = [
        name_emoji + name,
        '\n',
        '\n',
        '&#9203; Длительность - {}'.format(duration),       #'&#9203;' is hourglass emoji
        '\n',
        '&#128197; Время контеста - {} - {}'.format(start_date, end_time),      #'&#128197;' is calendar emoji
        '\n',
        '&#9888; Начало в вашем регионе - {}'.format(str(short_url))        #'&#9888;' is warning sign emoji
    ]
    return post


with open('contest_ids.json', 'r') as conid:
    a = json.loads(conid.read())


while True:
    req = requests.get('http://codeforces.com/api/contest.list?lang=ru')
    reqres = json.loads(req.text)
    phase = reqres['result'][START_ID]['phase']
    contest_id = reqres['result'][START_ID]['id']
    relativeTime = reqres['result'][START_ID]['relativeTimeSeconds']
    publish_date = reqres['result'][START_ID]['startTimeSeconds']
    if reqres['result'][START_ID]['startTimeSeconds'] == reqres['result'][START_ID+1]['startTimeSeconds']:
        contest_id_1 = reqres['result'][START_ID+1]['id']
        contest_url = str('http://codeforces.com/contests/{}{}{}'.format(str(contest_id), '%2C', str(contest_id_1)))
        a.append(contest_id, contest_id_1)
    else:
        contest_url = 'http://codeforces.com/contests/{}'.format(str(contest_id))
    short_url = short_tnd_url(START_ID)
    if phase == 'BEFORE' and contest_id not in a: 
        a.append(contest_id)
        post = format_post(START_ID)
        post  = ' '.join(post)
        api.wall.post(
            owner_id = GROUP_ID, 
            from_group = 1, 
            message = post,
            v = 5.71,
            publish_date = publish_date,
            attachments = contest_url,
        )
        
        with open('contest_ids.json', 'a') as conid:
            json.dumps(contest_id, conid)
        START_ID += 1
    
    else:
        START_ID = 0
    
    time.sleep(60)
