#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests"""

import os
import unittest
from wpparser import parse


class ParseTestCase(unittest.TestCase):
    def test_parse(self):
        result = parse("./blog.wordpress.2014-09-26.xml")

        assert len(result["posts"]) is 2
        assert result["blog"]["title"] == "Blog"
        assert len(result["categories"]) is 1
        assert len(result["tags"]) is 1


if __name__ == "__main__":
    unittest.main()
