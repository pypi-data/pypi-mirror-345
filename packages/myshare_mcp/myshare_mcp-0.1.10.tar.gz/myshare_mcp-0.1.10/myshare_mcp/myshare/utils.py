# Add these imports at the top
from datetime import datetime, timedelta
import os

# support logging
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    log_file = os.path.join(log_dir, "myshare.log")
    os.makedirs(log_dir, exist_ok=True)

    # Log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Log to file (with rotation)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB per file
        backupCount=5,          # Keep 5 backups
    )
    file_handler.setFormatter(formatter)

    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,     # Default level
        handlers=[console_handler, file_handler]
    )

def get_working_days(start_date: str, end_date: str) -> int:
    """Calculate number of working days between two dates"""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    days = 0
    current = start
    
    while current <= end:
        # Skip weekends (5 = Saturday, 6 = Sunday)
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    
    return days

def get_symbol_base(symbol: str) -> str:
    """
    Get the base symbol from a stock symbol with market suffix.
    """
    if "." in symbol:
        base, market = symbol.split(".")
        # Handle Hong Kong market special case (HKI -> HK)
        if market == "HKI":
            market = "HK"
        return base
    else:
        # Raise exception if no market suffix is present
        raise ValueError(f"Symbol '{symbol}' must include a market suffix (e.g., .SH, .SZ, .HK)")

def normalize_symbol(symbol: str) -> tuple[str, str]:
    """
    Normalize a stock symbol by determining its market and returning the standardized format.
    
    Args:
        symbol (str): Stock symbol with or without market suffix (e.g., "601006.SH" or "601006")
    
    Returns:
        tuple[str, str]: A tuple containing (normalized_symbol, market_suffix)
        
    Examples:
        >>> normalize_symbol("601006")
        ("601006.SH", "SH")
        >>> normalize_symbol("601006.SH")
        ("601006.SH", "SH")
        >>> normalize_symbol("0700.HK")
        ("0700.HK", "HK")
    """
    # If symbol already contains market suffix
    if "." in symbol:
        base, market = symbol.split(".")
        # Handle Hong Kong market special case (HKI -> HK)
        if market == "HKI":
            market = "HK"
        return f"{base}.{market}", market

    # No market suffix, determine by pattern
    # Shanghai market (starts with 6)
    if symbol.startswith("6") and len(symbol) == 6:
        return f"{symbol}.SH", "SH"
    
    # Beijing market (starts with 43, 83, 87, 88, 92 or 93)
    if (symbol.startswith("4") or symbol.startswith("8") or symbol.startswith("9")) and len(symbol) == 6:
        return f"{symbol}.BJ", "BJ"
    
    # Shenzhen market (starts with 000 or 300)
    # TODO: check "00" at the moment, should be "000", "001", "002", "300"
    if len(symbol) == 6 and (symbol.startswith("00") or symbol.startswith("300")):
        return f"{symbol}.SZ", "SZ"
    
    # Hong Kong market (typically 4 digits)
    if len(symbol) == 4 and symbol.isdigit():
        return f"{symbol}.HK", "HK"
    
    # Singapore market (typically ends with SI)
    if symbol.endswith("SI"):
        return symbol, "SI"
    
    # US market (default case - assume any remaining symbols are US stocks)
    return f"{symbol}.US", "US"

# 示例调用
if __name__ == "__main__":
    start_date = "20230101"
    end_date = "20230110"
    working_days = get_working_days(start_date, end_date)
    print(f"从 {start_date} 到 {end_date} 的工作日数量: {working_days}")