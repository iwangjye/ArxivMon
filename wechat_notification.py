import json
import time
import requests

class WechatNotification():
    def send(self, to, status, papers):
        if to == '':
            raise Exception('sendkey is null')

        desp = ''
        cur_time = time.strftime("%m-%d %H:%M", time.localtime())
        if status == 0:
            title = 'new papers found -- ' + cur_time
            for p in papers:
                desp += '---' + '\n\n#### [' + p[3] + '](' + p[2] + ')' + '\n\n *' + p[4] \
                + '*' + '\n\n' + '##### Submitted: ' + p[6] + '\n\n---'
        elif status == 1:
            title = 'can not access arxiv website!'
        elif status == 2:
            title = 'no new paper found.'
            desp = 'time: ' + cur_time
        
        data = {'title': title, 'desp': desp}
        url = 'https://sctapi.ftqq.com/{}.send'.format(to)
        r = requests.post(url, data=data)

        res = json.loads(r.text)
        if res['data']['errno'] != 0:
            raise Exception(res['data']['errmsg'])