import pytest
from myshare_mcp.myshare.utils import normalize_symbol
from myshare_mcp.myshare.utils import get_symbol_base

@pytest.mark.parametrize(
    "symbol, expected",
    [
        # Test cases with market suffix
        ("430564.BJ", ("430564.BJ", "BJ")),
        ("835185.BJ", ("835185.BJ", "BJ")),
        ("920002.BJ", ("920002.BJ", "BJ")),
        ("601006.SH", ("601006.SH", "SH")),
        ("0700.HK", ("0700.HK", "HK")),
        ("AAPL.US", ("AAPL.US", "US")),
        ("D05.SI", ("D05.SI", "SI")),
        ("000001.SZ", ("000001.SZ", "SZ")),
        ("300001.SZ", ("300001.SZ", "SZ")),
        ("601006.HKI", ("601006.HK", "HK")),  # Special case for HKI -> HK

        # Test cases without market suffix
        ("430564", ("430564.BJ", "BJ")),  # Beijing market
        ("835185", ("835185.BJ", "BJ")),  # Beijing market
        ("920002", ("920002.BJ", "BJ")),  # Beijing market
        ("601006", ("601006.SH", "SH")),  # Shanghai market
        ("000001", ("000001.SZ", "SZ")),  # Shenzhen market
        ("300001", ("300001.SZ", "SZ")),  # Shenzhen market
        ("0700", ("0700.HK", "HK")),      # Hong Kong market
        ("AAPL", ("AAPL.US", "US")),      # US market
        ("D05", ("D05.US", "US")),        # Default to US market
    ]
)
def test_normalize_symbol(symbol, expected):
    assert normalize_symbol(symbol) == expected
    
@pytest.mark.parametrize(
    "symbol, expected",
    [
        ("601006.SH", "601006"),  # Shanghai market
        ("000001.SZ", "000001"),  # Shenzhen market
        ("0700.HK", "0700"),      # Hong Kong market
        ("AAPL.US", "AAPL"),      # US market
        ("D05.SI", "D05"),        # Singapore market
        ("601006.HKI", "601006"), # Special case for HKI -> HK
    ]
)
def test_get_symbol_base_valid(symbol, expected):
    assert get_symbol_base(symbol) == expected

@pytest.mark.parametrize(
    "symbol",
    [
        "601006",       # Missing market suffix
        "000001",       # Missing market suffix
        "AAPL",         # Missing market suffix
        "0700",         # Missing market suffix
        "D05",          # Missing market suffix
    ]
)
def test_get_symbol_base_invalid(symbol):
    with pytest.raises(ValueError, match=f"Symbol '{symbol}' must include a market suffix"):
        get_symbol_base(symbol)
