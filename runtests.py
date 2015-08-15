#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests"""

import unittest
from wpparser import parse


class ParseTestCase(unittest.TestCase):
    def test_parse(self):
        result = parse("./blog.wordpress.2014-09-26.xml")

        assert len(result["posts"]) is 3
        assert result["blog"]["title"] == "Blog"
        assert len(result["categories"]) is 1
        assert len(result["tags"]) is 1

    def test_attachment_metadata(self):
        result = parse("./blog.wordpress.2014-09-26.xml")

        post = result["posts"][2]

        assert "postmeta" in post
        assert "attached_file" in post["postmeta"]
        assert "attachment_metadata" in post["postmeta"]

        attached_file = post["postmeta"]["attached_file"]
        assert attached_file == "logo-promo.png"


if __name__ == "__main__":
    unittest.main()
