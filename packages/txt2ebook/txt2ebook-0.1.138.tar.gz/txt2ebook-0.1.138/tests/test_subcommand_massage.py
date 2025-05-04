# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-rl", "--regex-delete-line"])
def test_delete_line_regex(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option, "我歌月徘徊")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "我歌月徘徊" not in content


@pytest.mark.parametrize("option", ["-rr", "--regex-replace"])
def test_single_replace_regex(tte, infile, option):
    txtfile = infile("sample.txt")

    tte("massage", txtfile, "-ow", option, "章", "章:")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "第1章:" in content
        assert "第2章:" in content
        assert "第3章:" in content


@pytest.mark.parametrize("option", ["-rd", "--regex-delete"])
def test_single_delete_regex(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option, "歌月", option, "我")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "徘徊，舞影零乱。" in content
