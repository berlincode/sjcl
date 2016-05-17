#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example for sjcl python module:

This module downloads all content of a blog from www.cyptedblog.com via the
JSON api, decrypts the SJCL encrpted posts/comments/images and saves both, the
encrypted and decrypted data to disk.

This module may also be used as a backup solution for cryptedblog.
"""

import os
import requests
import json
from sjcl import SJCL
import base64

URL_API = '%(server)s/api/blog/v1.0'
URL_POST = URL_API + '/blog/%(blog)s/posts?offset=%(offset)d&limit=%(limit)d'
URL_COMMENT = URL_API + '/blog/%(blog)s/posts/%(post)s/comments?offset=%(offset)d&limit=%(limit)d'
URL_IMAGES = URL_API + '/images/%(image)s'


def write_file(fname_parts, content):
    """ write a file and create all needed directories """

    fname_parts = [str(part) for part in fname_parts]
    # try to create the directory
    if len(fname_parts) > 1:
        try:
            os.makedirs(os.path.join(*fname_parts[:-1]))
        except OSError:
            pass
    # write file
    fhandle = open(os.path.join(*fname_parts), "w")
    fhandle.write(content)
    fhandle.close()


class Cryptedblog():
    """ This module downloads all content of a blog from www.cyptedblog.com via the
    JSON api, decrypts the SJCL encrpted posts/comments/images and saves both, the
    encrypted and decrypted data to disk.

    This module may also be used as a backup solution for cryptedblog.
    """

    def __init__(self, server, blog, shared_secret, limit=5):
        self.server = server
        self.blog = blog
        self.shared_secret = shared_secret
        self.limit = limit  # how many posts/comments to fetch with one request
        self.sjcl = SJCL()

    def download_images(self, fname_parts, key_image):
        response = requests.get(URL_IMAGES % {
            "server": self.server,
            "image": key_image
        })
        data = response.json()
        # special case: images are server from blobstrore and do normally not
        # contain a "success" field !!!
        if not data.get("success", True):
            raise Exception("error image")
        write_file(
            fname_parts + ["images-encrypted.json"],
            json.dumps(data, indent=4, sort_keys=True)
        )

        images = json.loads(
            self.sjcl.decrypt(
                data,
                self.shared_secret
            )
        )
        for (counter, image) in enumerate(images):
            write_file(
                fname_parts + ["image_%02d.json" % counter],
                json.dumps(image, indent=4, sort_keys=True)
            )
            # data uri of inline images starts like "data:image/jpeg;base64,"
            file_type = image["data"].split("image/")[1].split(";")[0]
            binary_data = base64.b64decode(image["data"].split("base64,")[1])
            write_file(
                fname_parts + ["image_%02d.%s" % (counter, file_type)],
                binary_data
            )

    def download_comments(self, key_post):
        offset = 0
        while True:

            response = requests.get(URL_COMMENT % {
                "server": self.server,
                "blog": self.blog,
                "post": key_post,
                "offset": offset,
                "limit": self.limit
            })
            data = response.json()
            if not data.get("success", False):
                raise Exception("error comment")

            for comment in data["data"]:
                key_comment = comment["comment"]
                fname_parts = [self.blog, "posts", key_post, "comments", key_comment]

                # write original data
                write_file(
                    fname_parts + ["comment.json"],
                    json.dumps(comment, indent=4, sort_keys=True)
                )
                # decrypt and write again
                comment["comment-decrypted"] = json.loads(
                    self.sjcl.decrypt(
                        comment["comment-encrypted"],
                        self.shared_secret
                    )
                )
                write_file(
                    fname_parts + ["comment-decrypted.json"],
                    json.dumps(comment, indent=4, sort_keys=True)
                )
                # get images
                if "images" in comment:
                    self.download_images(fname_parts + ["images"], comment["images"])

                offset += 1

            if len(data["data"]) == 0:
                break

    def download_posts(self):
        offset = 0
        while True:
            response = requests.get(URL_POST % {
                "server": self.server,
                "blog": self.blog,
                "offset": offset,
                "limit": self.limit
            })
            data = response.json()
            for post in data["data"]:
                key_post = post["post"]
                fname_parts = [self.blog, "posts", key_post]

                # write original data
                write_file(
                    fname_parts + ["post.json"],
                    json.dumps(post, indent=4, sort_keys=True)
                )

                # decrypt and write again
                post["post-decrypted"] = json.loads(
                    self.sjcl.decrypt(
                        post["post-encrypted"],
                        self.shared_secret
                    )
                )
                write_file(
                    fname_parts + ["post_decrypted.json"],
                    json.dumps(post, indent=4, sort_keys=True)
                )

                # get images
                if "images" in post:
                    self.download_images(fname_parts + ["images"], post["images"])

                self.download_comments(key_post)
                offset += 1

            # break if there are no further posts
            if len(data["data"]) == 0:
                break

if __name__ == "__main__":
    cr = Cryptedblog(
        server="http://www.cryptedblog.com",
        blog="test-blog",
        shared_secret="YourSharedSecret",
    )
    cr.download_posts()
