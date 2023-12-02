#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from string import punctuation

import mwparserfromhell as mwp
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

_quote_pattern = re.compile(r"<(q|blockquote)>.*</(q|blockquote)>", re.DOTALL)
_wikiquote_pattern = re.compile(r"{{Wikiquote\|(?P<title>.+?)}}", re.I)
_timestamp_pattern = re.compile(
    r"[0-9]{2}:[0-9]{2}, [0-9]{1,2} [^\W\d]+ [0-9]{4} \(UTC\)", re.I
)
_user_link_pattern = re.compile(r"(User_talk|User):(=?P<title>.+)", re.I)
_user_mention_pattern = re.compile(r"@\[?(?P<title>.+?)\]?", re.I)

MARKUP_TO_HTML = {
    "#": "li",
    "*": "li",
    ";": "dt",
    ":": "dd",
}


def is_timestamp(node_str):
    return node_str and _timestamp_pattern.match(node_str) is not None


def is_quote(node_str):
    return node_str and (
            _quote_pattern.match(node_str) is not None
            or _wikiquote_pattern.match(node_str) is not None
    )


def is_user_link(node_str):
    return node_str and _user_link_pattern.match(node_str) is not None


def is_user_mention(node_str):
    return node_str and _user_mention_pattern.match(node_str) is not None


# def try_parse_date(date_str):
#     import dateparser
#     try:
#         dt = dateparser.parse(date_str)
#         return True, dt.strftime("%Y-%m-%d %H:%M:%S")
#     except:
#         return False, None


def unicode_normalize(text):
    """
    check in the future(because it seems that it removes some necessary characters)
    unicodedata.normalize('NFKD', text)")
    :param text:
    :return:
    """
    text = (
        text.strip()
        .replace("\ufeff", "")
        .replace("\n", " ")
        .replace("\xa0", " ")
        .replace("\u200a", " ")
        .replace("\u200b", "")
        .strip()
    )
    text = text.replace("\u200f", "").replace("\u200e", "").strip()
    return text


def clean_text(text):
    text = unicode_normalize(text)
    text = text.replace("<blockquote>", "'")
    text = text.replace("</blockquote>", "'")
    text = text.replace("{{", "'")  # fix, should be processed as mwt.nodes.Template
    text = text.replace("}}", "'")  # fix, should be processed as mwt.nodes.Template
    text = text.replace("<br>", "\n")
    text = text.replace("<br />", "\n")
    text = text.rstrip("-")
    text = text.replace("reply to|",
                        "@")  # fix, should be processed as mwt.nodes.Template
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text().strip()
    return text


def is_open_parenthesis(node_str):
    return node_str.strip().endswith("(")


def is_close_parenthesis(node_str):
    # mwp parser doesn't parse close parenthesis correctly
    return node_str.strip().startswith(")")


def is_open_wikiquote(node_str):
    return node_str.strip().startswith("{{")


def is_closing_wikiquote(node_str):
    return node_str.strip().startswith("}}")


def parse_section_line(stack, level=0):
    level = 0
    if stack:
        fisrt_node = stack[0]
        wikitext = str(fisrt_node).strip()
        level = len(wikitext) - len(wikitext.lstrip(":;*"))

    data = {
        "text": None,
        "links": None,
        "date": None,
        "level": level,
        # "raw": wikitext
    }
    contents = []
    while stack:
        node = stack.pop(0)
        node_str = str(node.strip()).strip().lstrip(":;*")
        if not node_str:
            continue
        elif isinstance(node, mwp.nodes.Template):
            if is_open_wikiquote(node_str):
                text = "{{"
                unclosed_wikiquote = 1
                while unclosed_wikiquote and stack:
                    node_str = str(stack.pop(0)).strip()
                    if is_closing_wikiquote(node_str):
                        text += "}}"
                        unclosed_wikiquote -= 1
                        if node_str.strip("}}"):
                            stack.insert(0, mwp.nodes.Template(node_str.lstrip("}}")))
                    else:
                        text += node_str
                contents.append(text.strip())
        elif isinstance(node, mwp.nodes.Text):
            if is_open_parenthesis(node_str):
                text = "("
                unclosed_parenthesis = 1
                while unclosed_parenthesis and stack:
                    node_str = str(stack.pop(0)).strip()
                    if is_close_parenthesis(node_str):
                        text += ")"
                        unclosed_parenthesis -= 1
                        if node_str.strip(")"):
                            stack.insert(0, mwp.nodes.Text(node_str.lstrip(")")))
                    else:
                        text += node_str
                node_str = text
            contents.append(node_str.strip())
        elif isinstance(node, mwp.nodes.ExternalLink):
            if node.title is None:
                contents.append(str(node.url))
            else:
                contents.append(f"[{str(node.title)}]({str(node.url)})")
        # elif isinstance(node, mwp.nodes.Comment):
        #     pass
        # elif isinstance(node, mwp.nodes.Argument):
        #     pass
        # elif isinstance(node, mwp.nodes.HTMLEntity):
        #     pass
        elif isinstance(node, mwp.nodes.Wikilink):
            if data["links"] is None:
                data["links"] = list()
            data["links"].append({"link": str(node.text), "text": str(node.title)})
            username = node.text or node.title
            contents.append(f"@{username}")
        elif isinstance(node, mwp.nodes.Tag):
            contents.append(str(node))
        else:
            contents.append(str(node))

    # backtracking to find author and date
    # assuming that date is last
    if contents:
        last_element = contents[-1]
        if is_timestamp(last_element):
            data["date"] = last_element
            contents.pop()
    if contents:
        last_element = contents[-1]
        before_last_element = contents[-2] if len(contents) > 1 else None
        if is_user_mention(last_element):
            data["author"] = last_element
            contents.pop()
        elif (
                is_user_mention(before_last_element)
                and last_element.startswith("(")
                and last_element.endswith(")")
        ):
            data["author"] = before_last_element
            contents.pop()
            contents.pop()

    data["text"] = clean_text("\n".join(contents))
    return data


def get_html_tag(markup):
    """Return the HTML tag associated with the given wiki-markup."""
    return MARKUP_TO_HTML[markup]


def is_new_post(node):
    node_str = str(node.strip()).strip()
    if all(c in MARKUP_TO_HTML for c in node_str):
        return True
    return False


def post_was_closed(node):
    # post is closed if last was timestamp
    if is_timestamp(str(node).strip()):
        return True
    else:
        return False


def iter_nodes(wikitext):
    """
    small fixes of mwp parser
    - e.g. it doesn't parse correctly close parenthesis
    - doesn't detect end of posts
    """

    def _fix_parenthesis(wikitext):
        stack = list(mwp.parse(wikitext).nodes)
        while stack:
            node = stack.pop(0)
            node_str = str(node.strip()).strip()
            if (
                    node_str
                    and isinstance(node, mwp.nodes.Text)
                    and is_open_parenthesis(node_str)
            ):
                text = "("
                unclosed_parenthesis = 1
                while unclosed_parenthesis and stack:
                    node_str = str(stack.pop(0)).strip()
                    if is_close_parenthesis(node_str):
                        text += ")"
                        unclosed_parenthesis -= 1
                        if node_str.strip(")"):
                            stack.insert(0, mwp.nodes.Text(node_str.lstrip(")")))
                    else:
                        text += node_str
                yield mwp.nodes.Text(text)
            elif isinstance(node, mwp.nodes.Tag) and node.closing_tag in (
                    "dd",
                    "li",
                    "dt",
            ):
                # skip nodes until we find the nodes that are not *;:
                text = node_str
                while stack:
                    node_str = str(stack.pop(0).strip()).strip()
                    if node_str not in "*;:":
                        if node_str:
                            stack.insert(0, mwp.nodes.Text(node_str))
                        break
                    text += node_str
                if text:
                    yield mwp.nodes.Text(text)
            else:
                yield node

    def _fix_incorret_splittings(wikitext):
        for node in _fix_parenthesis(wikitext):
            if node.strip() and isinstance(node, mwp.nodes.Text) and "UTC" in str(node):
                # fix incorrect parsing of mwp , - detect timestamp and put break line
                texts = []
                for line in str(node).split("\n"):
                    if is_timestamp(line.strip(punctuation)):
                        texts.append(mwp.nodes.Text(line))
                        texts.append(mwp.nodes.Text("\n"))
                    else:
                        texts.append(mwp.nodes.Text(line))
                for node in texts:
                    yield node
            else:
                yield node

    group = []
    head = None
    for node in _fix_incorret_splittings(wikitext):
        if isinstance(node, mwp.nodes.Heading):
            if group:
                yield head, group
                group = []
            head = str(node.strip()).strip("=").strip()
        else:
            group.append(node)
    if group:
        yield head, group


# fmt: off
def posts_splitter(nodes):
    level, group = 0, []
    for node in nodes:
        node_str = str(node.strip()).strip()
        if is_new_post(node):
            level = len(node_str) - len(node_str.lstrip(":;*"))
            if group:
                yield level, group
                level, group, = 0, []
            group.append(node)
        elif post_was_closed(node):
            if group:
                group.append(node)
                yield level, group
                level, group, = 0, []
        elif node_str:
            group.append(node)
    if group:
        yield level, group


# fmt: on


def parse_wikitalk(wikitext):
    wikitext = wikitext.strip()
    for header, group_nodes in iter_nodes(wikitext):
        if header is None:
            continue
        heading = {
            "title": header,
            "posts": list(),
        }
        for current_level, nodes_posts in posts_splitter(group_nodes):
            post = parse_section_line(nodes_posts, current_level)
            if post["text"]:
                heading["posts"].append(post)
        yield heading
