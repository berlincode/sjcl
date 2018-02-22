#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from sjcl import SJCL

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_encrypt_decrypt(self):
        message = b"secret message to encrypt"
        cyphertext = SJCL().encrypt(message, "shared_secret")
        self.assertEqual(
            SJCL().decrypt(cyphertext, "shared_secret"),
            message
        )

    def test_decrypt(self):
        cyphertext = {
            'ks': 128,
            'cipher': 'aes',
            'mode': 'ccm',
            'v': 1,
            'adata': '',
            'iv': 'fR4fZKbjsZOrzDyjCYdEQw==',
            'salt': '5IiimlH8JvY=',
            'ts': 64,
            'iter': 1000,
            'ct': 'V8BYrUdurq1/Qx/EX8EBliKDKa6XB93dZ6QOFSelw77Q'
        }
        self.assertEqual(
            SJCL().decrypt(cyphertext, "shared_secret"),
            b"secret message to encrypt"
        )

    def test_gcm_mode_encrypt_decrypt(self):
        message = b"secret message to encrypt"
        cyphertext = SJCL().encrypt(message, "shared_secret", mode="gcm")

        self.assertEqual(
            SJCL().decrypt(cyphertext, "shared_secret"),
            message
        )

    def test_gcm_decrypt(self):
        cyphertext = {
            "iv": "oi51KdYi8av0PysYeCDDiw==",
            "v":1,
            "iter":10000,
            "ks":256,
            "ts":128,
            "mode":"gcm",
            "adata":"",
            "cipher":"aes",
            "salt": "C4DRJM5AH+A=",
            "ct": "KIINDGEQO63pY2mFIWpOuWgx2RAnfU0rhKU="
        }
        self.assertEqual(
            SJCL().decrypt(cyphertext, "vYHOPyQ7Q6NOfm6zkT44IE2SVv+52arqCOv7cDfMApI="),
            b"test paste"
        )

if __name__ == '__main__':
    unittest.main()
