from datetime import datetime
import akshare as ak
import pandas as pd

def get_xq_symbol(stock_code):
    """
    将股票代码转换为雪球 API 的格式。

    参数:
        stock_code (str): 股票代码，例如 '600325'。

    返回:
        str: 符合雪球 API 格式的股票代码，例如 'SH600325'。
    """
    # 确保输入是字符串类型
    stock_code = str(stock_code).strip()
    
    # 检查股票代码长度是否为 6 位
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise ValueError(f"无效的股票代码：{stock_code}。股票代码必须是 6 位数字。")
    
    # 判断交易所前缀
    if stock_code.startswith("6"):
        prefix = "SH"  # 上海证券交易所
    else:
        prefix = "SZ"  # 深圳证券交易所
    
    # 拼接并返回雪球 API 格式
    return f"{prefix}{stock_code}"

def get_stock_spot_xq(symbol: str) -> dict:
    """
    获取股票的实时数据。

    参数:
        symbol (str): 股票代码，例如 '600325'。

    返回:
        dict: 包含股票实时数据的字典。
    """
    # 将股票代码转换为雪球 API 格式
    xq_symbol = get_xq_symbol(symbol)
    
    # 使用 AKShare 获取实时数据
    spot_data = ak.stock_individual_spot_xq(symbol=xq_symbol)
    
    # 检查返回的数据是否有效
    if 'item' not in spot_data or 'value' not in spot_data:
        raise Exception(f"从 AKShare 获取的数据格式不正确：缺少 'item' 或 'value' 键。响应内容：{spot_data}")
    
    # 将数据转换为字典格式
    spot_dict = dict(zip(spot_data['item'], spot_data['value']))
    
    return {
        "symbol": symbol,
        "market": "SH" if xq_symbol.startswith("SH") else "SZ",
        "名称": spot_dict.get('名称', ""),
        "现价": float(spot_dict.get('现价', 0.0)),
        "开盘": float(spot_dict.get('开盘', 0.0)),
        "最高": float(spot_dict.get('最高', 0.0)),
        "最低": float(spot_dict.get('最低', 0.0)),
        "市盈率-TTM": float(spot_dict.get('市盈率-TTM', 0.0)),
        "市净率": float(spot_dict.get('市净率', 0.0)),
        "总市值": float(spot_dict.get('总市值', 0.0)),
        "timestamp": datetime.now()
    }

# 示例调用
if __name__ == "__main__":
    # 输入股票代码
    examples = ["600325", "000001", "300059"]
    
    for example in examples:
        xueqiu_code = get_xq_symbol(example)
        print(f"股票代码 {example} 转换为雪球 API 格式: {xueqiu_code}")