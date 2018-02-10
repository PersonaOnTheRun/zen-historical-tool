from flask import Flask, render_template, request, Response, redirect, url_for
app = Flask(__name__)

#Version 0.1.1

import requests
import datetime
import csv
s = requests.Session()

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

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



@app.route('/',methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/paperwallet',methods = ['GET'])
def paperwallet():
    return render_template('paper_wallet.html')



@app.route('/transactions/',methods = ['GET','POST'])
def transactions():
    if request.method == 'POST':
        zenaddress = request.form['zenaddress']
        return redirect(url_for('result', zenaddress=zenaddress))
    return render_template('transactions.html')


@app.route('/transactions/<zenaddress>',methods = ['GET'])
def result(zenaddress):
    rowlist = zendata(zenaddress)
    def generate():
        for row in rowlist:
            yield ','.join(str(v) for v in row) + '\n'
    return Response(generate(), mimetype='text/csv')



if __name__ == '__main__':
   app.run(debug = False)
