# Wikitalk Parser

Development in progress, so might be unstable.

## Description

Simple parser of the wikitext markup language from wiki talk pages. 

## Usage

```python
from wikitalk_parser import parse_wikitalk

wikitalk_text = """
== Age at inauguration ==

Under "Early actions", I would like to add the fact that Trump was the oldest person in US history to be sworn in as president. This appears quiet significant. The same has been done on [[Ronald Reagan|Reagan]]'s page. My proposal can be seen below:

70 years old at the time, he became the [[List of presidents of the United States by age|oldest person to assume the U.S. presidency]], surpassing [[Ronald Reagan]] who took office at age 69 [[First inauguration of Ronald Reagan|in 1981]]; this ranking would at age 78 be passed on to Joe Biden [[Inauguration of Joe Biden|in 2021]]. [[User:Marginataen|Marginataen]] ([[User talk:Marginataen|talk]]) 14:28, 26 November 2023 (UTC)
:LOr "he became the oldest until he was not", seems to me to not really be very informative. [[User:Slatersteven|Slatersteven]] ([[User talk:Slatersteven|talk]]) 14:30, 26 November 2023 (UTC)

:Have we the same written about Reagan (nearly 70, in January 1981) & before that W. Harrison (68, in March 1841)? Kinda irrelevant trivia, since Biden (passed 78, in January 2021) too office. [[User:GoodDay|GoodDay]] ([[User talk:GoodDay|talk]]) 14:33, 26 November 2023 (UTC)
::We have the same or similar at [[Ronald Reagan]] only because this user recently added it, so it should be reverted. [[User:Zaathras|Zaathras]] ([[User talk:Zaathras|talk]]) 14:39, 26 November 2023 (UTC)
""".strip()

parsed = parse_wikitalk(wikitalk_text)
for section in parsed:
    print(section["title"])
    for post in section["posts"]:
        print(post)
    print()
# Age at inauguration
# {'text': 'Under "Early actions", I would like to add the fact that Trump was the oldest person in US history to be sworn in as president. This appears quiet significant. The same has been done on @Reagan \'s page. My proposal can be seen below:  70 years old at the time, he became the @oldest person to assume the U.S. presidency , surpassing @Ronald Reagan who took office at age 69 @in 1981 this ranking would at age 78 be passed on to Joe Biden @in 2021 .', 'links': [{'link': 'Reagan', 'text': 'Ronald Reagan'}, {'link': 'oldest person to assume the U.S. presidency', 'text': 'List of presidents of the United States by age'}, {'link': 'None', 'text': 'Ronald Reagan'}, {'link': 'in 1981', 'text': 'First inauguration of Ronald Reagan'}, {'link': 'in 2021', 'text': 'Inauguration of Joe Biden'}, {'link': 'Marginataen', 'text': 'User:Marginataen'}], 'date': '14:28, 26 November 2023 (UTC)', 'level': 0, 'author': '@Marginataen'}
# {'text': 'LOr "he became the oldest until he was not", seems to me to not really be very informative.', 'links': [{'link': 'Slatersteven', 'text': 'User:Slatersteven'}], 'date': '14:30, 26 November 2023 (UTC)', 'level': 1, 'author': '@Slatersteven'}
# {'text': 'Have we the same written about Reagan (nearly 70, in January 1981) & before that W. Harrison (68, in March 1841)? Kinda irrelevant trivia, since Biden (passed 78, in January 2021) too office.', 'links': [{'link': 'GoodDay', 'text': 'User:GoodDay'}], 'date': '14:33, 26 November 2023 (UTC)', 'level': 1, 'author': '@GoodDay'}
# {'text': 'We have the same or similar at @Ronald Reagan only because this user recently added it, so it should be reverted.', 'links': [{'link': 'None', 'text': 'Ronald Reagan'}, {'link': 'Zaathras', 'text': 'User:Zaathras'}], 'date': '14:39, 26 November 2023 (UTC)', 'level': 2, 'author': '@Zaathras'}
```

Getting wikitext from wiki page:

```python
from wikitalk_parser import parse_wikitalk, get_wikitalk

wikitext = get_wikitalk("Elon_Musk", language="en")
parsed = parse_wikitalk(wikitext)
for section in parsed:
    print(section["title"])
    for post in section["posts"]:
        print(post)
    print()
```

### Getting wikitalk through API

```python
from wikitalk_parser import get_wikitalk_from_api

threads = get_wikitalk_from_api("Elon_Musk", language="en")
for thread in threads:
    print(thread)
```

