import requests
import datetime
import csv
s = requests.Session()

zenaddress = 'znffypWbhE9TTsTZWTEW83USivQj5ryH9ZD'
tx = 'b641371a6e06b7ec585f15dd2f25e312c2dfc64f23b6ed9744e92de894c51c23'

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

def txprocess(tx,zenaddress):
    pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
    preq = requests.Request('GET', pricelink)
    pr = preq.prepare()
    pricedata = s.send(pr)
    pricedata = pricedata.json()
    pricedata = pricedata['Data']
    print(tx)
    link2 = 'https://explorer.zensystem.io/insight-api-zen/tx/'
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
    print(closeprice,row)
    value = float(closeprice)*float(row[1])
    row.append(value)
    print(row)
    try:
        if tempdata['vin'][0]['addr'] == zenaddress:
            print("self send, skipping")
        else:
            print("added to rowlist")
    except IndexError:




def zendata(zenaddress):
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
    for tx in link1data['transactions']:
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
        print(closeprice,row)
        value = float(closeprice)*float(row[1])
        row.append(value)
        try:
            if tempdata['vin'][0]['addr'] == zenaddress:
                print("self send, skipping")
            else:
                row.append(tempdata['vin'][0]['addr'])
                rowlist.append(row)
                print("added to rowlist")
        except IndexError:
            print("z_address")
            row.append('zk transaction')
            rowlist.append(row)
    return rowlist
