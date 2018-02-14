from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
from celery import Celery
import requests
import datetime
import csv
import os
import random


#Version 0.2.5

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
    # get the price data
    pricedata = pricedata['Data']

    s = requests.Session()
    link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress
    req = requests.Request('GET', link)
    r = req.prepare()
    data = s.send(r)
    data = data.json()
    pages = data['pagesTotal']
    rowlist = [["Time", "Amount", "Price","Value","Tx Address","Sender"]]

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
            row.append(tx['txid'])
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
