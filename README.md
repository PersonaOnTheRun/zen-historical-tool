# ZenCash Historical Price Tool

The purpose of this tool is to make it easier during tax season to figure out your earnings from mining and secure node returns. This tool includes all inbound transactions and ignores all outbound transactions. It also ignores inbound transactions originating from your own ZenCash Address. (This usually happens when excess fees are returned to your address.)


## Details

The closing price of the date of the transaction is used. For example if you received ZenCash at 2:15pm on 01/05/2018, the price returned in the .csv will be the closing price of 01/05/2018. While this is not perfectly accurate, it is a shortcut taken for simplicity. In the next update I will try to return hourly data.

## Sources

- [CryptoCompare](https://www.cryptocompare.com/)
- [ZenSystem's Explorer](https://explorer.zensystem.io/)
