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

if __name__ == '__main__':
    unittest.main()
