from flask import Flask, request
import requests
import json
import logging
import datetime

app = Flask(__name__)

wwxRobot = 'http://htnginx88.qyapi.weixin.qq.com.local/cgi-bin/webhook/send?key=xxxxxx-xxxx-xxxxx-xxxx-xxxxx'

wxHeader = {'Content-type': 'application/json'}

msgTitle = {'firing': '<font color=\"warning\"> ===系统警报===</font> \n',
            'resolved': '<font color=\"info\">---警报解除---</font> \n'}


def localDT(alertdt):
    utc_dt = datetime.datetime.strptime(alertdt[:19], '%Y-%m-%dT%H:%M:%S')
    local_dt = utc_dt + datetime.timedelta(hours=8)
    return datetime.datetime.strftime(local_dt, '%Y-%m-%d %H:%M:%S')


@app.route('/WWXMSG', methods=['POST', 'GET'])
def wwxmsg():
    logging.basicConfig(filename='post.log', level=logging.DEBUG)
    postData = str(request.data, encoding='utf-8')
    logging.info(postData)
    jsonData = json.loads(postData)
    msgBody = {"msgtype": "markdown", "markdown": {"content": ""}}
    msgAlert = []
    for alert in jsonData['alerts']:
        msgAlert.append(msgTitle[alert['status']])
        if alert['status'] == 'firing':
            msgAlert.append('**' + alert['annotations']['summary'] + '**\n')
            msgAlert.append('发生时间: ' + localDT(alert['startsAt']) + '\n')
        else:
            msgAlert.append(alert['annotations']['summary'] + '\n')
            msgAlert.append('发生时间: ' + localDT(alert['startsAt']) + '\n')
            msgAlert.append('解除时间: ' + localDT(alert['endsAt']) + '\n')
        msgAlert.append(''.join(['> ' + k + ': <font color="comment">' + v + '</font>\n' for k, v in alert['labels'].items()]))
        msgAlert.append('\n\n')
    
    msgBody['markdown']['content'] = ''.join(msgAlert)
    r = requests.post(wwxRobot, data=json.dumps(msgBody), headers=wxHeader)
    return r.text


@app.route('/')
def index():
    return '<title>Robot</title><h1>WeChat Work Robot</h1>'


if __name__ == '__main__':
    app.debug = True
    app.run()
