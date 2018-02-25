import hashlib, binascii
import random


def make_salt(len):
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = ''.join(random.choice(ALPHABET) for i in range(len))
    return str.encode(chars)

def make_password():
    password = input("What is your password? ")
    return str.encode(password)


"saltLength": 32

# generateHash(options.algorithm, salt, password, options.iterations)

seedHex = hashlib.pbkdf2_hmac('sha512', make_password(), make_salt(32), 100000)
binascii.hexlify(seedHex)


import os, binascii
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
backend = default_backend()
# Salts should be randomly generated
salt = os.urandom(32)
# derive
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=backend
)
key = kdf.derive(b"my great password")
keyHex = binascii.hexlify(key)





# verify
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=backend
)
kdf.verify(b"my great password", key)





wif = generateNewAddress(1, userInfo.pass)[0]
pk = zencashjs.address.WIFToPrivKey(wif);
addr = zencashjs.address.pubKeyToAddr(zencashjs.address.privKeyToPubKey(pk, true));

function generateNewAddress(count, password) {
    let i;
    let seedHex = passwordHash.generate(password, {
        "algorithm": "sha512",
        "saltLength": 32
    }).split("$")[3];

    // chains
    let hdNode = bitcoin.HDNode.fromSeedHex(seedHex);
    let chain = new bip32utils.Chain(hdNode);

    for (i = 0; i < count; i += 1) {
        chain.next();
    }

    // Get private keys from them - return privateKeys
    return chain.getAll().map(function (x) {
        return chain.derive(x).keyPair.toWIF();
    });
}
