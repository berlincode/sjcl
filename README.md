Python-SJCL
===========

[![Travis CI](https://travis-ci.org/berlincode/sjcl.svg?branch=master&style=flat)](https://travis-ci.org/berlincode/sjcl)
[![Python versions](https://img.shields.io/pypi/pyversions/sjcl.svg)](https://pypi.python.org/pypi/sjcl/)
[![new-style BSD](https://img.shields.io/pypi/l/sjcl.svg)](https://github.com/berlincode/sjcl/blob/master/LICENSE.txt)

Decrypt and encrypt messages compatible to the "Stanford Javascript Crypto
Library (SJCL)" message format. This is a wrapper around pycrypto.

This module was created while programming and testing the encrypted
blog platform on cryptedblog.com which is based on sjcl.

Typical usage may look like this:

```python
    #!/usr/bin/env python

    from sjcl import SJCL

    cyphertext = SJCL().encrypt("secret message to encrypt", "shared_secret")

    print cyphertext
    print SJCL().decrypt(cyphertext, "shared_secret")
```

Public repository
-----------------

[https://github.com/berlincode/sjcl](https://github.com/berlincode/sjcl)


License
-------

Code and documentation copyright Ulf Bartel. Code is licensed under the
[new-style BSD license](./LICENSE.txt).

