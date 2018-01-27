import vk
import json
import datetime   
import requests
import time

accesstoken = 'accesstoken_sample'
group_id = 
session = vk.Session(access_token=accesstoken)
api = vk.API(session)
i = 0
with open('contest_ids.json', 'r') as conid:
    a = json.loads(conid.read())

def format_post(a, i):
    a = [str(reqres['result'][i]['name']),
    '\n',
    '\n',
    'Длительность - ' + str(reqres['result'][i]['durationSeconds'] // 3600),
    ':',
    str(reqres['result'][i]['durationSeconds'] % 3600 // 60),
    '\n',
    'Время контеста - ' + str((
        datetime.datetime.fromtimestamp(
            int(reqres['result'][i]['startTimeSeconds'])
        ).strftime('%d.%m.%Y %H:%M')
    )) + ' GMT' ]
    return a

while True:
    req = requests.get('http://codeforces.com/api/contest.list?')
    req = req.text
    reqres = json.loads(req)
    phase = reqres['result'][i]['phase']
    contest_id = reqres['result'][i]['id']
    relativeTime = reqres['result'][i]['relativeTimeSeconds']
    if phase == 'BEFORE' and contest_id not in a and relativeTime >= -172800: 
        a.append(reqres['result'][i]['id'])
        post = 0
        post = format_post(post, i)
        post  = ' '.join(post)
        api.wall.post(
            owner_id = group_id, 
            from_group = 1, 
            message = post
        )
        with open('contest_ids.json', 'a') as conid:
            json.dump(contest_id, conid)
        i += 1
    else:
        i = 0
    time.sleep(60)
