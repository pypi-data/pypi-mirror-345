from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
from myshare_mcp.myshare.utils import normalize_symbol, get_symbol_base

def get_stock_spot_dc(symbol: str) -> dict:
    """
    获取股票的实时数据。
    
    参数:
        symbol (str): 股票代码，例如 '600325'。
    
    返回:
        dict: 包含股票实时数据的字典。
    """
    symbol_f, market = normalize_symbol(symbol)
    symbol = get_symbol_base(symbol_f)
    yesterday = datetime.now() - timedelta(days=10)
    start_date = yesterday.strftime('%Y%m%d')

    today = datetime.now()
    end_date = today.strftime('%Y%m%d')
 
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period="daily",
        adjust=""
    )    
    # 使用 AKShare 获取实时数据
    spot_data = df.iloc[-1].to_dict()

    stock_info_df = ak.stock_individual_info_em(symbol)
    
    # 检查返回的数据是否有效
    if 'item' not in stock_info_df or 'value' not in stock_info_df:
        raise Exception(f"从 AKShare 获取的数据格式不正确：缺少 'item' 或 'value' 键。响应内容：{stock_info_df}")
    
    # 将数据转换为字典格式
    spot_dict = dict(zip(stock_info_df['item'], stock_info_df['value']))
    
    return {
        "symbol": symbol,
        "market": market,
        "名称": spot_dict.get('股票简称', ""),
        "现价": float(spot_data.get('收盘', 0.0)),
        "开盘": float(spot_data.get('开盘', 0.0)),
        "最高": float(spot_data.get('最高', 0.0)),
        "最低": float(spot_data.get('最低', 0.0)),
        "市盈率-TTM": 0,
        "市净率": 0,
        "总市值": float(spot_dict.get('总市值', 0.0)),
        "timestamp": datetime.now()
    }