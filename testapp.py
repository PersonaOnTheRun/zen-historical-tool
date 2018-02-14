#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:38:18 2018

@author: cammilligan
"""

import requests
import datetime

zenaddress = 'znffypWbhE9TTsTZWTEW83USivQj5ryH9ZD'
zenaddress = 'znh538G66Tf55auwaXYdng5wx9G1YERidHq'

def apicall3():
    s = requests.Session()
    pricelink = 'https://min-api.cryptocompare.com/data/histoday?fsym=ZEN&tsym=USD&allData=true&aggregate=1&e=CCCAGG'
    preq = requests.Request('GET', pricelink)
    pr = preq.prepare()
    pricedata = s.send(pr)
    pricedata = pricedata.json()
    pricedata = pricedata['Data']
    return pricedata

def search(txtime, pricedata):
    return [element for element in pricedata if datetime.datetime.fromtimestamp(element['time']).strftime('%x') == txtime]

pricedata = apicall3()

def apicall0(zenaddress,pricedata):
    s = requests.Session()
    link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress
    req = requests.Request('GET', link)
    r = req.prepare()
    data = s.send(r)
    data = data.json()
    pages = data['pagesTotal']
    print(pages)
    rowlist = [["Time", "Amount", "Price","Value","Sender"]]
    for n in range(pages):
        page = n+1
        print(page)
        link = 'https://explorer.zensystem.io/insight-api-zen/txs/?address='+zenaddress+'&pageNum='+str(page)
        req = requests.Request('GET', link)
        r = req.prepare()
        txdata = s.send(r)
        txdata = txdata.json()
        #txdata is a list of <= 10 transactions
        
        for tx in txdata['txs']:
            row = []
            txtime = tx['time']
            row.append(datetime.datetime.fromtimestamp(txtime).strftime('%Y-%m-%d'))
            for n in tx['vout']:
                if n['scriptPubKey']['addresses'][0] == zenaddress:
                    row.append(n['value'])
            closeprice = search(txtime, pricedata)
            try:
                closeprice = closeprice[0]['close']
            except IndexError:
                closeprice = 0
            row.append(closeprice)
            value = float(closeprice)*float(row[1])
            row.append(value)
            try:
                if tx['vin'][0]['addr'] != zenaddress:
                    row.append(tx['vin'][0]['addr'])
                    rowlist.append(row)
            except IndexError:
                row.append('zk transaction')
                rowlist.append(row)
    return rowlist
    
    
    
#data['txs'][0]['vout'][0]['value']