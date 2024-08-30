from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List

import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


app = FastAPI()


class PagesIn(BaseModel):
    pages: str = Field(examples=["https://www.tomaszbak.com/"])
    remove_tags: List[str] = Field([], examples=[["header", "footer", "img"]])


@app.post("/pages/")
async def pages2md(params: PagesIn) -> List[str]: 
    """
    Convert list of URL to list of markdown
    For each page:
    - removes tags like "header", "footer", "img" passed via "remove_tags"
    - adds MDX Frontmatter with url, title and desciption for each markdown
    """ 

    results = []
    for url in params.pages.split("\n"):
        try:
            content = get_content(url)

            soup = BeautifulSoup(content, "html.parser")
            content = remove_tags(soup, ["header", "footer", "img"])
            header = meta_header(url, get_meta(soup))

            results.append(header + md(content, escape_misc=False))
        except requests.exceptions.RequestException as e:
            results.append(str(e))

    return map(strip_newlines, results)


@app.get("/page/{_:path}",response_class=PlainTextResponse)
async def page2md(request: Request):
    """
    Convert URL passed to /page/[url] to markdown
    Removes tags like "header", "footer", "img"
    Adds MDX Frontmatter with url, title and desciption
    """ 

    url = request.url.path[6:]

    try:
        content = get_content(url)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail=str(e))

    soup = BeautifulSoup(content, "html.parser")
    content = remove_tags(soup, ["header", "footer", "img"])
    header = meta_header(url, get_meta(soup))

    return strip_newlines(header + md(content, escape_misc=False))


"""
Utils
"""
def get_content(url: str):
    response = requests.get(url)
    response.raise_for_status()

    return response.content

def strip_newlines(s):
    return re.sub(r"\n\n+", "\n\n", s)

def meta_header(url: str, meta):
    header = "---\nurl: " + url + "\n"
    for k, v in meta.items(): header = header + str(k) + ": " + str(v) + "\n"
    header = header + "---\n"

    return header

def get_meta(soup):
    from collections import OrderedDict
    meta = OrderedDict({})
    title = soup.find("title")
    meta["title"] = title and title.string
    description = soup.find('meta',attrs={'name':'description'})
    meta["description"] = description and description["content"]

    return meta

def remove_tags(soup, tags):
    for img in soup.find_all('img', {'src': re.compile(r'(data:image\/[^;]+;base64.*?)')}):
        img.decompose()

    for data in soup(['svg', 'style', 'script', 'head.link'] + tags):
        data.decompose()

    return str(soup)
