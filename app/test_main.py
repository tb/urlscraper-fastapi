import pytest
from fastapi.testclient import TestClient
import requests
import requests_mock
from difflib import ndiff, SequenceMatcher

from src.main import app

client = TestClient(app)


def test_post():
    with requests_mock.Mocker() as m:
        m.register_uri('GET', 'https://www.tomaszbak.com/', text=page1_html())
        response = client.get("/page/https://www.tomaszbak.com/")
        assert response.status_code == 200
        assert_text_match(page1_markdown(), response.content.decode())

def test_posts():
    with requests_mock.Mocker() as m:
        m.register_uri('GET', 'https://www.tomaszbak.com/', text=page1_html())
        m.register_uri('GET', 'http://github.com/', text=page2_html())
        response = client.post("/pages/", json={
            "pages": "https://www.tomaszbak.com/\nhttp://github.com/"
        })
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert_text_match(page1_markdown(), response.json()[0])
        assert_text_match(page2_markdown(), response.json()[1])

def test_posts_with_error():
    with requests_mock.Mocker() as m:
        m.register_uri('GET', 'http://wp.pl/', exc=requests.exceptions.Timeout)
        m.register_uri('GET', 'http://github.com/', text=page2_html())
        response = client.post("/pages/", json={
            "pages": "http://wp.pl/\nhttp://github.com/"
        })
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert_text_match("", response.json()[0])
        assert_text_match(page2_markdown(), response.json()[1])


"""
Utils
"""
def assert_text_match(s1, s2):
    ratio = SequenceMatcher(None, s1, s2).ratio() 
    if ratio < 1:
      diff = '\n'.join(list(ndiff(
          str(s1).splitlines(),
          str(s2).splitlines()
      )))
      print(diff)

    assert ratio == 1

def page1_html():
    return """<!DOCTYPE html>
<html>
<head><title>Page Title</title></head>
<body>
<h1>My First Heading</h1>
<p>My first paragraph.</p>
<img src="img.png" alt="Some image">
</body>
</html>"""

def page1_markdown():
   return """---
url: https://www.tomaszbak.com/
title: Page Title
description: None
---

Page Title

My First Heading
================

My first paragraph.

"""

def page2_html():
    return """<!DOCTYPE html>
<html>
<head>
<title>Github Page Title</title>
<meta name="description" content="Github Description" />
</head>
<body>
<h1>Github</h1>
<h2>Let's build from here</h2>
</body>
</html>"""

def page2_markdown():
   return """---
url: http://github.com/
title: Github Page Title
description: Github Description
---

Github Page Title

Github
======

Let's build from here
---------------------

"""
