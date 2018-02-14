from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
from celery import Celery
import requests
import datetime
import csv
import os
import random


#Version 0.2.2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config["REDIS_URL"] = os.environ.get("REDIS_URL")

# Celery configuration
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

# def apicall1(zenaddress):
#     s = requests.Session()
#     link1 = 'https://explorer.zensystem.io/insight-api-zen/addr/'+zenaddress
#     req = requests.Request('GET', link1)
#     r = req.prepare()
#     link1data = s.send(r)
#     link1data = link1data.json()
#     txlist = link1data['transactions']
#     # we were figuring out a way to increment the count1 and count2 on each loop. results caps at 1000
#     # thicc
#     while len(txlist) % 1000 == 0:
#         count1 = len(txlist) + 1
#         count2 = count1 + 1000
#         txlink = 'https://explorer.zensystem.io/insight-api-zen/addr/'+str(zenaddress)+'?from='+str(count1)+'&to='+str(count2)
#         req = requests.Request('GET', txlink)
#         r = req.prepare()
#         txdata = s.send(r)
#         txdata = txdata.json()
#         txresult = txdata['transactions']
#         txlist = txlist + txresult
#     return txlist


# def apicall2(tx,zenaddress,pricedata):
#     s = requests.Session()
#     link2 = 'https://explorer.zensystem.io/insight-api-zen/tx/'
#     print(tx)
#     row = []
#     templink = link2+tx
#     print(templink)
#     req = requests.Request('GET', templink)
#     r = req.prepare()
#     tempdata = s.send(r)
#     tempdata = tempdata.json()
#     txtime = datetime.datetime.fromtimestamp(tempdata['time']).strftime('%x')
#     print(txtime)
#     row.append(datetime.datetime.fromtimestamp(tempdata['time']).strftime('%Y-%m-%d'))
#     for n in tempdata['vout']:
#         if n['scriptPubKey']['addresses'][0] == zenaddress:
#             row.append(n['value'])
#     closeprice = search(txtime, pricedata)
#     try:
#         closeprice = closeprice[0]['close']
#     except IndexError:
#         closeprice = 0
#     row.append(closeprice)
#     value = float(closeprice)*float(row[1])
#     row.append(value)
#     try:
#         if tempdata['vin'][0]['addr'] != zenaddress:
#             row.append(tempdata['vin'][0]['addr'])
#             return row
#     except IndexError:
#         row.append('zk transaction')
#         return row

# def apicall3():
#     s = requests.Session()
#     pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
#     preq = requests.Request('GET', pricelink)
#     pr = preq.prepare()
#     pricedata = s.send(pr)
#     pricedata = pricedata.json()
#     pricedata = pricedata['Data']
#     print('WHY AINT I WORKING')
#     print(pricedata)
#     return pricedata

@celery.task(bind=True)
def zentask(self,zenaddress):
    print(zenaddress)
    #silly stuff
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Launching']
    adjective = ['master', 'scientific', 'tranquil', 'obsolete', 'imaginary']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'teleportation device']
    message = ''
    self.update_state(state='PENDING')
    s = requests.Session()
    pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
    preq = requests.Request('GET', pricelink)
    pr = preq.prepare()
    pricedata = s.send(pr)
    pricedata = pricedata.json()
    pricedata = pricedata['Data']

    s = requests.Session()
    link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress
    req = requests.Request('GET', link)
    r = req.prepare()
    data = s.send(r)
    data = data.json()
    pages = data['pagesTotal']
    rowlist = [["Time", "Amount", "Price","Value","Sender"]]

    total = pages
    print("total number of pages: ",pages)
    i = 0

    for n in range(pages):
        i = i + 1
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})

        page = n
        print(page)
        if total == 1:
            link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress
        else:
            link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress+'&pageNum='+str(page)
        req = requests.Request('GET', link)
        r = req.prepare()
        txdata = s.send(r)
        txdata = txdata.json()
        #txdata is a list of <= 10 transactions
        for tx in txdata['txs']:

            row = []
            txtime = tx['time']
            txtime = datetime.datetime.fromtimestamp(txtime).strftime('%x')
            row.append(datetime.datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d'))
            print("appended time")
            for n in tx['vout']:
                if n['scriptPubKey']['addresses'][0] == zenaddress:
                    row.append(n['value'])
                    print("appended value")
            closeprice = search(txtime, pricedata)
            try:
                closeprice = closeprice[0]['close']
            except IndexError:
                closeprice = 0
            row.append(closeprice)
            print("appended closeprice")
            value = float(closeprice)*float(row[1])
            row.append(value)
            print("appended value")
            try:
                if tx['vin'][0]['addr'] != zenaddress:
                    row.append(tx['vin'][0]['addr'])
                    rowlist.append(row)
                    print("appended rowlist with zenaddress")
            except IndexError:
                row.append('zk transaction')
                rowlist.append(row)
                print("appended rowlist with zk transaction")
    self.update_state(state='COMPLETE')
    print(rowlist)
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': rowlist}
    # s = requests.Session()
    # link1 = 'https://explorer.zensystem.io/insight-api-zen/addr/'+zenaddress
    #
    # link2 = 'https://explorer.zensystem.io/insight-api-zen/tx/'
    # pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
    #
    # req = requests.Request('GET', link1)
    # r = req.prepare()
    # link1data = s.send(r)
    # link1data = link1data.json()
    # preq = requests.Request('GET', pricelink)
    # pr = preq.prepare()
    # pricedata = s.send(pr)
    # pricedata = pricedata.json()
    # for tx in link1data['transactions']:
    #     #silly stuff
    #     i = i+1
    #     if not message or random.random() < 0.25:
    #         message = '{0} {1} {2}...'.format(random.choice(verb),
    #                                           random.choice(adjective),
    #                                           random.choice(noun))
    #     self.update_state(state='PROGRESS',
    #                       meta={'current': i, 'total': total,
    #                             'status': message})
    #     print(tx)
    #     row = []
    #     templink = link2+tx
    #     req = requests.Request('GET', templink)
    #     r = req.prepare()
    #     tempdata = s.send(r)
    #     tempdata = tempdata.json()
    #     txtime = datetime.datetime.fromtimestamp(tempdata['time']).strftime('%x')
    #     row.append(datetime.datetime.fromtimestamp(tempdata['time']).strftime('%Y-%m-%d'))
    #     for n in tempdata['vout']:
    #         if n['scriptPubKey']['addresses'][0] == zenaddress:
    #             row.append(n['value'])
    #     closeprice = search(txtime, pricedata)
    #     closeprice = closeprice[0]['close']
    #     row.append(closeprice)
    #     value = float(closeprice)*float(row[1])
    #     row.append(value)
    #     try:
    #         if tempdata['vin'][0]['addr'] != zenaddress:
    #             row.append(tempdata['vin'][0]['addr'])
    #             rowlist.append(row)
    #     except IndexError:
    #         row.append('zk transaction')
    #         rowlist.append(row)



@app.route('/',methods = ['GET'])
def home():
    return render_template('index.html')


@app.route('/transactions/',methods = ['GET','POST'])
def transactions():
    return render_template('transactions.html')

@app.route('/zendata/',methods = ['POST'])
def zendata():
    if request.method == 'POST':
        print('request received')
    zenaddress = request.form.get('zenaddress')
    task = zentask.delay(zenaddress)
    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = zentask.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
