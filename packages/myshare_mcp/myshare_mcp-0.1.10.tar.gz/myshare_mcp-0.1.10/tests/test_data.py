import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from myshare_mcp.myshare.data import get_stock_spot, StockSpot, get_stock_history, StockHistory

@pytest.fixture
def mock_db_session():
    with patch('myshare_mcp.myshare.data.SessionLocal') as mock:
        session = MagicMock()
        mock.return_value.__enter__.return_value = session
        yield session

@pytest.fixture
def mock_akshare():
    with patch('myshare_mcp.myshare.data.ak') as mock:
        yield mock

@pytest.fixture
def mock_xq_symbol():
    with patch('myshare_mcp.myshare.data.get_xq_symbol') as mock:
        mock.return_value = 'SH123456'
        yield mock

def test_get_stock_spot_cached(mock_db_session):
    # Setup mock cached data
    cached = StockSpot(
        symbol='000001',
        name='Test Stock',
        current_price=10.0,
        open_price=9.0,
        high_price=11.0,
        low_price=8.0,
        pe_ratio=15.0,
        pb_ratio=1.5,
        market_cap=1000000.0,
        timestamp=datetime.now()
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = cached

    # Test
    result = get_stock_spot('000001')

    # Verify
    assert result['symbol'] == '000001'
    assert result['name'] == 'Test Stock'
    assert result['source'] == 'cache'
    assert result['current_price'] == 10.0

def test_get_stock_spot_new(mock_db_session, mock_akshare, mock_xq_symbol):
    # Setup mock db (no cache)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Setup mock AKShare response
    mock_akshare.stock_individual_spot_xq.return_value = {
        'item': ['名称', '现价', '开盘', '最高', '最低', '市盈率-TTM', '市净率', '总市值'],
        'value': ['Test Stock', '10.0', '9.0', '11.0', '8.0', '15.0', '1.5', '1000000.0']
    }

    # Test
    result = get_stock_spot('000001')

    # Verify
    assert result['symbol'] == '000001'
    assert result['name'] == 'Test Stock'
    assert result['source'] == 'akshare'
    assert result['current_price'] == 10.0
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_stock_spot_malformed_response(mock_db_session, mock_akshare, mock_xq_symbol):
    # Setup mock db (no cache)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Setup mock malformed AKShare response
    mock_akshare.stock_individual_spot_xq.return_value = {}

    # Test
    with pytest.raises(Exception) as exc_info:
        get_stock_spot('000001')
    
    assert "Malformed response from AKShare" in str(exc_info.value)

def test_get_stock_spot_update_existing(mock_db_session, mock_akshare, mock_xq_symbol):
    # Setup mock db (existing record)
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        None,  # First call for cache check
        True   # Second call for existing check
    ]

    # Setup mock AKShare response
    mock_akshare.stock_individual_spot_xq.return_value = {
        'item': ['名称', '现价', '开盘', '最高', '最低', '市盈率-TTM', '市净率', '总市值'],
        'value': ['Test Stock', '10.0', '9.0', '11.0', '8.0', '15.0', '1.5', '1000000.0']
    }

    # Test
    result = get_stock_spot('000001')

    # Verify
    assert result['symbol'] == '000001'
    assert result['source'] == 'akshare'
    mock_db_session.query.return_value.filter.return_value.update.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.fixture
def mock_working_days():
    with patch('myshare_mcp.myshare.data.get_working_days') as mock:
        mock.return_value = 5
        yield mock

def test_get_stock_history_cached(mock_db_session, mock_working_days):
    # Setup mock cached data
    cached_history = [
        StockHistory(
            symbol='000001',
            date=datetime.strptime('20230101', '%Y%m%d'),
            open_price=10.0,
            close_price=11.0,
            high_price=12.0,
            low_price=9.0,
            volume=1000.0
        )
    ] * 5  # Match expected_days=5
    mock_db_session.query.return_value.filter.return_value.all.return_value = cached_history

    # Test
    result = get_stock_history('000001', '20230101', '20230105')

    # Verify
    assert len(result) == 5
    assert result[0]['source'] == 'cache'
    assert result[0]['open'] == 10.0
    assert result[0]['close'] == 11.0
    mock_working_days.assert_called_once()

def test_get_stock_history_new(mock_db_session, mock_working_days):
    # Setup mock db (no cache)
    mock_db_session.query.return_value.filter.return_value.all.return_value = []

    # Setup mock AKShare response
    mock_df = pd.DataFrame({
        '日期': ['2023-01-01'],
        '开盘': [10.0],
        '收盘': [11.0],
        '最高': [12.0],
        '最低': [9.0],
        '成交量': [1000.0]
    })
    with patch('myshare_mcp.myshare.data.ak') as mock_ak:
        mock_ak.stock_zh_a_hist.return_value = mock_df

        # Test
        result = get_stock_history('000001', '20230101', '20230105')

        # Verify
        assert len(result) == 1
        assert result[0]['source'] == 'akshare'
        #assert result[0]['open'] == 10.0
        #assert result[0]['close'] == 11.0
        mock_db_session.commit.assert_called_once()

def test_get_stock_history_malformed_response(mock_db_session, mock_working_days):
    # Setup mock db (no cache)
    mock_db_session.query.return_value.filter.return_value.all.return_value = []

    # Setup mock malformed AKShare response
    mock_df = pd.DataFrame({
        'wrong_column': ['2023-01-01']
    })
    with patch('myshare_mcp.myshare.data.ak') as mock_ak:
        mock_ak.stock_zh_a_hist.return_value = mock_df

        # Test
        with pytest.raises(KeyError) as exc_info:
            get_stock_history('000001', '20230101', '20230105')
        
        assert "日期" in str(exc_info.value)

def test_get_stock_history_merge(mock_db_session, mock_working_days):
    # Setup mock db (no cache)
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    mock_db_session.merge.side_effect = lambda x: x

    # Setup mock AKShare response
    mock_df = pd.DataFrame({
        '日期': ['2023-01-01', '2023-01-02'],
        '开盘': [10.0, 11.0],
        '收盘': [11.0, 12.0],
        '最高': [12.0, 13.0],
        '最低': [9.0, 10.0],
        '成交量': [1000.0, 1100.0]
    })
    with patch('myshare_mcp.myshare.data.ak') as mock_ak:
        mock_ak.stock_zh_a_hist.return_value = mock_df

        # Test
        result = get_stock_history('000001', '20230101', '20230105')

        # Verify
        assert len(result) == 2
        assert mock_db_session.merge.call_count == 2
        assert result[0]['open'] == 10.0
        assert result[1]['open'] == 11.0
