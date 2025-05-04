import pygnuregex


def test_compile():
    p = pygnuregex.compile(b"f\\(oo\\)[0-9]+")
    assert p.pb
    assert not p.span()
    assert p.nsub() == 1


def test_match():
    p = pygnuregex.compile(b"f\\(oo\\)[0-9]+")
    assert p.match(b"foo123") == 6
    assert p.match(b"foo") == -1


def test_search():
    p = pygnuregex.compile(b"f\\(oo\\)[0-9]+")
    result = p.search(b"hello foo123!")
    assert result == 6
    assert p.nsub() == 1
    s = p.span()
    assert len(s) == 2
    assert s[0] == (6, 12)
    assert s[1] == (7, 9)
