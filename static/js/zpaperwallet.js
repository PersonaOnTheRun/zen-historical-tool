const zencashjs = require("zencashjs");
const passwordHash = require("password-hash");
const bitcoin = require("bitcoinjs-lib");
const bip32utils = require("bip32-utils");
const Qrcode = require("qrcode");
const jsPDF = require("jspdf");

function exportPaperWallet() {
  var wif = bitcoin.ECPair.makeRandom().toWIF();
  // console.log(wif);
  const privateKey = zencashjs.address.WIFToPrivKey(wif);
  // console.log(privateKey);
  const pubKey = zencashjs.address.privKeyToPubKey(privateKey, true);
  // console.log(pubKey);
  const tAddr = zencashjs.address.pubKeyToAddr(pubKey);
  // console.log(tAddr);

  function createQrCodeAsync(text) {
      const opts = {
          margin: 1,
      };
      return Qrcode.toDataURL(text, opts);
  }

  function renderWallet(pkHexQrCode, tAddrQrCode) {
      const name = $('#paperWalletName').val();
      // console.log(name);
      // console.log("Rendering Wallet");
      const pdf = new jsPDF(); // a4
      const pdfW = pdf.internal.pageSize.width;
      const pdfH = pdf.internal.pageSize.height;

      function centeredText(text, y) {
          const textWidth = pdf.getStringUnitWidth(text) * pdf.internal.getFontSize() / pdf.internal.scaleFactor;
          const x = (pdfW - textWidth) / 2;
          pdf.text(x, y, text);
          return 10; // FIXME find out height from font metrics
      }

      function centerSquareImage(img, format, y) {
          const WIDTH = 80;
          const x = (pdfW - WIDTH)/2;
          pdf.addImage(img, format, x, y, WIDTH, WIDTH);
          return WIDTH + 10; // FIXME + 10
      }

      let y = 10;

      if (name)
          y += centeredText("ZENCASH WALLET " + name, y);
      else
          y += centeredText("ZENCASH WALLET", y);
      y += 10;

      y += centeredText("PRIVATE KEY", y);
      y += 0;
      y += centeredText(wif, y);
      y += 0;
      y += centerSquareImage(pkHexQrCode, "JPEG", y);
      y += 10;
      y += centeredText("T-ADDRESS", y);
      y += 0;
      y += centeredText(tAddr, y);
      y += 0;
      y += centerSquareImage(tAddrQrCode, "JPEG", y);

      let filename;
      if (name)
          filename = `zencash-wallet-${name}.pdf`;
      else
          filename = `zencash-wallet-${tAddr}.pdf`;

      pdf.save(filename);
  }

  Promise.all([ createQrCodeAsync(wif), createQrCodeAsync(tAddr) ])
      .then(results => {
          const privKeyQrCode = results[0];
          const tAddrQrCode = results[1];
          return renderWallet(privKeyQrCode, tAddrQrCode);
      });
}

module.exports = {
  exportPaperWallet
}
