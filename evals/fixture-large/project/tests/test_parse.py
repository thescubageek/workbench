from linkcrawl.parse.css_refs import extract_css_refs
from linkcrawl.parse.dispatch import can_extract, extract_links
from linkcrawl.parse.html_links import extract_html_links
from linkcrawl.parse.markdown_links import extract_markdown_links

BASE = "https://example.com/docs/"


def urls(links):
    return [link.url for link in links]


def test_html_collects_common_attributes():
    page = """<html><head><link rel="stylesheet" href="/s.css"></head>
<body>
<a href="intro.html">Intro</a>
<a href="mailto:x@example.com">mail</a>
<a href="#top">top</a>
<img src="img/a.png" srcset="img/a.png 1x, img/a@2x.png 2x">
<script src="https://cdn.example.net/app.js"></script>
</body></html>"""
    assert urls(extract_html_links(page, BASE)) == [
        "https://example.com/s.css",
        "https://example.com/docs/intro.html",
        "https://example.com/docs/img/a.png",
        "https://example.com/docs/img/a@2x.png",
        "https://cdn.example.net/app.js",
    ]


def test_html_base_tag_changes_resolution():
    page = '<base href="https://example.com/v2/"><a href="page">p</a>'
    assert urls(extract_html_links(page, BASE)) == ["https://example.com/v2/page"]


def test_html_nofollow_can_be_skipped():
    page = '<a rel="nofollow" href="/ad">ad</a><a href="/ok">ok</a>'
    assert urls(extract_html_links(page, BASE, follow_nofollow=False)) == [
        "https://example.com/ok"]


def test_html_line_numbers():
    page = "<p>\n\n<a href='/x'>x</a>"
    assert extract_html_links(page, BASE)[0].line == 3


def test_markdown_ignores_fenced_code_and_keeps_lines():
    text = "[a](a.md)\n```\n[b](b.md)\n```\n[ref]: https://example.org/r\n"
    links = extract_markdown_links(text, BASE)
    assert urls(links) == ["https://example.com/docs/a.md", "https://example.org/r"]
    assert [link.line for link in links] == [1, 5]


def test_markdown_image_and_autolink():
    links = extract_markdown_links("![i](p.png) <https://example.net/x>", BASE)
    assert [link.kind for link in links] == ["md-image", "md-autolink"]


def test_css_url_and_import():
    css = '@import "base.css";\n/* url(ignored.png) */\n.a { background: url(\'i/bg.png\') }'
    assert urls(extract_css_refs(css, BASE)) == [
        "https://example.com/docs/base.css",
        "https://example.com/docs/i/bg.png",
    ]


def test_dispatch_by_type_and_extension():
    assert can_extract("text/html", "https://example.com/")
    assert can_extract("", "https://example.com/readme.md")
    assert not can_extract("image/png", "https://example.com/a.png")
    body = b"\xef\xbb\xbf<a href='/z'>z</a>"
    assert urls(extract_links(body, "text/html", BASE)) == ["https://example.com/z"]
