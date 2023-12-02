#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import pywikibot as pw

_link_pattern = re.compile(r"https?://\S+")


def is_link(title):
    return title and _link_pattern.match(title) is not None


def get_wikitalk(title, *, language):
    if is_link(title):
        title = title.split("/")[-1]
    page = pw.Page(pw.Site(language, 'wikipedia'), title)
    talk_page = page.toggleTalkPage()
    text = talk_page.get()
    return text
