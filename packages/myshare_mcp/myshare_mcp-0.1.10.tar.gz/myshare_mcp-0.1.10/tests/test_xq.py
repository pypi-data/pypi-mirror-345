import pytest
from myshare_mcp.myshare.xq import get_xq_symbol

def test_get_xq_symbol_sh():
    assert get_xq_symbol("600325") == "SH600325"
    assert get_xq_symbol("600000") == "SH600000"

def test_get_xq_symbol_sz():
    assert get_xq_symbol("000001") == "SZ000001"
    assert get_xq_symbol("300059") == "SZ300059"

def test_get_xq_symbol_with_integer():
    assert get_xq_symbol(600325) == "SH600325"
    assert get_xq_symbol(300059) == "SZ300059"

def test_get_xq_symbol_with_spaces():
    assert get_xq_symbol(" 600325 ") == "SH600325"
    assert get_xq_symbol(" 000001 ") == "SZ000001"

def test_get_xq_symbol_invalid_length():
    with pytest.raises(ValueError):
        get_xq_symbol("12345")
    with pytest.raises(ValueError):
        get_xq_symbol("1234567")

def test_get_xq_symbol_invalid_format():
    with pytest.raises(ValueError):
        get_xq_symbol("12A345")
    with pytest.raises(ValueError):
        get_xq_symbol("ABCDEF")