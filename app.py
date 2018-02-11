from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
from celery import Celery
import requests
import datetime
import csv
import os
import random


#Version 0.2.1

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

@celery.task(bind=True)
def zentask(self,zenaddress):
    print(zenaddress)
    #silly stuff
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''

    self.update_state(state='PENDING')
    s = requests.Session()
    link1 = 'https://explorer.zensystem.io/insight-api-zen/addr/'+zenaddress

    link2 = 'https://explorer.zensystem.io/insight-api-zen/tx/'
    pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'

    req = requests.Request('GET', link1)
    r = req.prepare()
    link1data = s.send(r)
    link1data = link1data.json()

    preq = requests.Request('GET', pricelink)
    pr = preq.prepare()
    pricedata = s.send(pr)
    pricedata = pricedata.json()
    pricedata = pricedata['Data']
    rowlist = [["Time", "Amount", "Price","Value","Sender"]]

    total = len(link1data['transactions'])
    i = 0

    for tx in link1data['transactions']:
        #silly stuff
        i = i+1
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        print(tx)
        row = []
        templink = link2+tx
        req = requests.Request('GET', templink)
        r = req.prepare()
        tempdata = s.send(r)
        tempdata = tempdata.json()
        txtime = datetime.datetime.fromtimestamp(tempdata['time']).strftime('%x')
        row.append(datetime.datetime.fromtimestamp(tempdata['time']).strftime('%Y-%m-%d'))
        for n in tempdata['vout']:
            if n['scriptPubKey']['addresses'][0] == zenaddress:
                row.append(n['value'])
        closeprice = search(txtime, pricedata)
        closeprice = closeprice[0]['close']
        row.append(closeprice)
        value = float(closeprice)*float(row[1])
        row.append(value)
        try:
            if tempdata['vin'][0]['addr'] != zenaddress:
                row.append(tempdata['vin'][0]['addr'])
                rowlist.append(row)
        except IndexError:
            row.append('zk transaction')
            rowlist.append(row)
    self.update_state(state='COMPLETE')
    print(rowlist)
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}


@app.route('/',methods = ['GET'])
def home():
    return render_template('index.html')


@app.route('/transactions/',methods = ['GET','POST'])
def transactions():
    return render_template('transactions.html')

@app.route('/zendata/',methods = ['POST'])
def zendata():
    if request.method == 'POST':
        print('is this actually happening?')
    zenaddress = request.form.get('zenaddress')
    print('the zenaddress is ',zenaddress)
    task = zentask.delay(zenaddress)
    print('did we make it here?')
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
   app.run(debug = True)



    # zenaddress = request.args.get('zenaddress', '')
    # result = task.zendata.delay(zenaddress)
    # result.wait()

    # , celery=result

# def generate():
#         for row in iter_all_rows():
#             yield ','.join(row) + '\n'
#
# 	headers = Headers()
# 	headers.add('Content-Disposition','attachment',filename=filename)
#
#     return Response(generate(), mimetype='text/csv',headers=headers)


# @app.route('/paperwallet',methods = ['GET'])
# def paperwallet():
#     return render_template('paper_wallet.html')

# @app.route('/transactions/',methods = ['GET','POST'])
# def transactions():
#     if request.method == 'POST':
#         zenaddress = request.form['zenaddress']
#         return redirect(url_for('result', zenaddress=zenaddress))
#     return render_template('transactions.html')
#
# @app.route('/transactions/<zenaddress>',methods = ['GET'])
# def result(zenaddress):
#     rowlist = zendata(zenaddress)
#     def generate():
#         for row in rowlist:
#             yield ','.join(str(v) for v in row) + '\n'
#     return Response(generate(), mimetype='text/csv')
