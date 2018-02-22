#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decrypt and encrypt messages compatible to the "Stanford Javascript Crypto
Library (SJCL)" message format.

This module was created while programming and testing the encrypted
blog platform on cryptedblog.com which is based on sjcl.
"""

import base64

from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Default tag length for differend AES modes
DEFAULT_TLEN = {
    AES.MODE_CCM: 64,
    AES.MODE_GCM: 128
}

# field explanation from Jay Tuley (jbtule)
# - see http://stackoverflow.com/a/13570154
#
#    ct: cipher-text your encrypted data, obviously
#    iv: Should be unique and not be reused with the same key for AES-CCM
#    salt: random, and is used to create the key from password with Pbkdf2
#    adata: additional authenticated data, is plain text data that you want
#        to include but ensure that it has not been tampered when using
#        AES-CCM. If you aren't ever going to include any data then you can
#        ignore it (you would have had to pass it with the plaintext in sjcl).
#
#    iter: iterations for Pbkdf2, this just needs to be high enough to slow
#        down bruteforce on your password needs to change with the speed of
#        hardware in the future.
#    ks: keysize to know what size key to generate with Pbkdf2, needs to change
#         with the amount of security in future
#    ts: tagsize to know what size authentication tag is part of your cipher
#         text
#    cipher: If you will only support AES, then you can just assume.
#    mode: if you will only support AES-CCM than you can just assume.
#    v: If you will only support one version of sjcl in the future than you can
#         just assume.


#def hex_string(array):
#    import binascii
#    return binascii.hexlify(bytearray(array))


def truncate_iv(iv, ol, tlen):  # ol and tlen in bits
    ivl = len(iv)  # iv length in bytes
    ol = (ol - tlen) // 8

    # "compute the length of the length" (see ccm.js)
    L = 2
    while (L < 4) and ((ol >> (8*L))) > 0:
        L += 1
    if L < 15 - ivl:
        L = 15 - ivl

    return iv[:(15-L)]


def get_aes_mode(mode):
    """Return pycrypto's AES mode, raise exception if not supported"""
    aes_mode_attr = "MODE_{}".format(mode.upper())
    try:
        aes_mode = getattr(AES, aes_mode_attr)
    except AttributeError:
        raise Exception(
            "Pycrypto/pycryptodome does not seem to support {}. ".format(aes_mode_attr) +
            "If you use pycrypto, you need a version >= 2.7a1 (or a special branch)."
        )
    return aes_mode


class SJCL(object):

    def __init__(self):
        self.salt_size = 8  # bytes
        self.prf = lambda p, s: HMAC.new(p, s, SHA256).digest()

    def decrypt(self, data, passphrase):
        if data["cipher"] != "aes":
            raise Exception("only aes cipher supported")

        aes_mode = get_aes_mode(data["mode"])
        tlen = data["ts"]

        if data["adata"] != "":
            raise Exception("additional authentication data not equal ''")

        if data["v"] != 1:
            raise Exception("only version 1 is currently supported")

        # Fix padding
        if aes_mode == AES.MODE_CCM:
            # not a multiple of 4, add padding:
            if len(data["salt"]) % 4:
                data["salt"] += '=' * (4 - len(data["salt"]) % 4)
        salt = base64.b64decode(data["salt"])

    #    print "salt", hex_string(salt)
        if len(salt) != self.salt_size:
            raise Exception("salt should be %d bytes long" % self.salt_size)

        dkLen = data["ks"]//8
        if dkLen != 16 and dkLen != 32:
            raise Exception("key length should be 16 bytes or 32 bytes")

        key = PBKDF2(
            passphrase,
            salt,
            count=data['iter'],
            dkLen=dkLen,
            prf=self.prf
        )
#       print "key", hex_string(key)
        if aes_mode == AES.MODE_CCM:
            # Fix padding
            if len(data["iv"]) % 4:
            # not a multiple of 4, add padding:
                data["iv"] += '=' * (4 - len(data["iv"]) % 4)
            if len(data["ct"]) % 4:
            # not a multiple of 4, add padding:
                data["ct"] += '=' * (4 - len(data["ct"]) % 4)

        ciphertext = base64.b64decode(data["ct"])
        iv = base64.b64decode(data["iv"])
#        print AES.block_size

        if aes_mode == AES.MODE_CCM:
            nonce = truncate_iv(iv, len(ciphertext)*8, data["ts"])
        else:
            nonce = iv

        # split tag from ciphertext (tag was simply appended to ciphertext)
        mac = ciphertext[-(data["ts"]//8):]
#        print len(ciphertext)
        ciphertext = ciphertext[:-(data["ts"]//8)]
#        print len(ciphertext)
#        print len(tag)

#        print "len", len(nonce)
        cipher = AES.new(key, aes_mode, nonce, mac_len=tlen // 8)
        plaintext = cipher.decrypt(ciphertext)

        cipher.verify(mac)

        return plaintext

    def encrypt(self, plaintext, passphrase, mode="ccm", count=10000, dkLen=16):
        # dkLen = key length in bytes
        aes_mode = get_aes_mode(mode)
        tlen = DEFAULT_TLEN[aes_mode]

        salt = get_random_bytes(self.salt_size)
        iv = get_random_bytes(16)  # TODO dkLen?

        key = PBKDF2(passphrase, salt, count=count, dkLen=dkLen, prf=self.prf)

        # TODO plaintext padding?
        if aes_mode == AES.MODE_CCM:
            nonce = truncate_iv(iv, len(plaintext) * 8, tlen)
        else:
            nonce = iv
    #    print len(nonce)

        cipher = AES.new(
            key,
            aes_mode,
            nonce,
            mac_len=tlen // 8
        )

        ciphertext = cipher.encrypt(plaintext)
        mac = cipher.digest()

        ciphertext = ciphertext + mac

        return {
            "salt": base64.b64encode(salt),
            "iter": count,
            "ks": dkLen*8,
            "ct": base64.b64encode(ciphertext),
            "iv": base64.b64encode(iv),
            "cipher": "aes",
            "mode": mode,
            "adata": "",
            "v": 1,
            "ts": tlen
            }
