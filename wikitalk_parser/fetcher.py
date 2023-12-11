#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from wikitalk_parser.parser import is_timestamp

PROJECT_DIR = Path(__file__).parent
os.environ['PYWIKIBOT_DIR'] = str(PROJECT_DIR)
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


TALK = {
    "he": "שיחה",
    "en": "Talk"
}


def get_wikitalk_api(title, *, language):
    if is_link(title):
        title = title.split("/")[-1]
    url = "https://{}.wikipedia.org/api/rest_v1/page/talk/{}%3A{}?redirect=true"
    url = url.format(language, TALK.get(language, "Talk"), title)

    response = requests.get(url)
    data = response.json()

    def mark_datetime(data):
        for topic in data["topics"]:
            for reply in topic["replies"]:
                if "<a" not in reply["html"]:
                    continue
                doc = BeautifulSoup(reply["html"], "html.parser")
                # find last <a> tag
                last_a = doc.find_all("a")[-1]
                # find text after last <a> tag
                timestamp = last_a.next_sibling
                if is_timestamp(str(timestamp)):
                    reply["timestamp"] = str(timestamp)
                else:
                    reply["timestamp"] = None
                if not last_a.has_attr("href"):
                    reply["username"] = None
                else:
                    href = last_a["href"]
                    username = href.split(":")[-1] if ":" in href else None
                    reply["username"] = username

        return data

    data = mark_datetime(data)
    topics = data["topics"]
    topics = [topic for topic in topics if topic["html"]]
    for topic in topics:
        topic.pop("shas", None)
        topic["title"] = topic.pop("html")
        for reply in topic["replies"]:
            reply.pop("sha", None)
    return topics
