def test_format():
    txt = render("mysite","summary",{"Docs":[("https://x","Title-desc")]})
    assert txt.startswith("# mysite"), "Missing H1"

def test_crawl_single():
    pages,_=crawl("https://example.com",limit=1)
    assert pages, "Crawler failed"
