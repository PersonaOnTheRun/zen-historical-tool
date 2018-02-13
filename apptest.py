import requests
import datetime
import csv
import os
import random

zenaddress='znffypWbhE9TTsTZWTEW83USivQj5ryH9ZD'

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

def apicall1(zenaddress):
    s = requests.Session()
    link1 = 'https://explorer.zensystem.io/insight-api-zen/addr/'+zenaddress
    req = requests.Request('GET', link1)
    r = req.prepare()
    link1data = s.send(r)
    link1data = link1data.json()
    results = link1data['transactions']
    # we were figuring out a way to increment the count1 and count2 on each loop. results caps at 1000
    # thicc
    while len(results) % 1000 == 0:
        count1 = len(results) + 1
        count2 = count1 + 1000
        print(count2)
        txlink = 'https://explorer.zensystem.io/insight-api-zen/addr/'+str(zenaddress)+'?from='+str(count1)+'&to='+str(count2)
        req = requests.Request('GET', txlink)
        r = req.prepare()
        txdata = s.send(r)
        txdata = txdata.json()
        txresult = txdata['transactions']
        results = results + txresult
    return results

def apicall2(tx):
    s = requests.Session()
    link2 = 'https://explorer.zensystem.io/insight-api-zen/tx/'
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
    return row


def apicall3():
    s = requests.Session()
    pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
    preq = requests.Request('GET', pricelink)
    pr = preq.prepare()
    pricedata = s.send(pr)
    pricedata = pricedata.json()
    pricedata = pricedata['Data']
    return pricedata


def zentask(zenaddress):
    print(zenaddress)
    #silly stuff
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''

    # self.update_state(state='PENDING')
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
        # self.update_state(state='PROGRESS',
                          # meta={'current': i, 'total': total,
                                # 'status': message})
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
    # self.update_state(state='COMPLETE')
    print(rowlist)
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': rowlist}
