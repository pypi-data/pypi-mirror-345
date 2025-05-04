from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import akshare as ak
import pandas as pd
import logging

from myshare_mcp.myshare.xq import get_xq_symbol, get_stock_spot_xq
from myshare_mcp.myshare.eastmoney import get_stock_spot_dc
from myshare_mcp.myshare.utils import get_working_days, normalize_symbol, get_symbol_base

logger = logging.getLogger(__name__)

# SQLite database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./finance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class StockSpot(Base):
    __tablename__ = "stock_spots"
    
    symbol = Column(String, primary_key=True)
    market = Column(String, primary_key=True)
    name = Column(String)
    current_price = Column(Float)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    market_cap = Column(Float)
    timestamp = Column(DateTime, index=True)

class StockHistory(Base):
    __tablename__ = "stock_histories"
    
    symbol = Column(String, primary_key=True)
    market = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)
    open_price = Column(Float)
    close_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Float)

# Create database tables
Base.metadata.create_all(bind=engine)

def get_stock_spot(symbol: str, market: str = "SH") -> Dict[str, Any]:
    """
    Get real-time stock data.

    Args:
        symbol (str): The stock symbol to fetch data for.
        market (str): The market of the stock. Defaults to "SH" for China market.
    Returns:
        Dict[str, Any]: A dictionary containing stock data.
    """

    symbol_f, market = normalize_symbol(symbol)
    symbol = get_symbol_base(symbol_f)
    with SessionLocal() as db:
        # Check cache first
        cached = db.query(StockSpot).filter(
            StockSpot.symbol == symbol,
            StockSpot.market == market,
            StockSpot.timestamp > datetime.now().replace(minute=0, second=0, microsecond=0)
        ).first()
        
        if cached:
            return {
                "symbol": cached.symbol,
                "market": cached.market,
                "name": cached.name,
                "current_price": cached.current_price,
                "open_price": cached.open_price,
                "high_price": cached.high_price,
                "low_price": cached.low_price,
                "pe_ratio": cached.pe_ratio,
                "pb_ratio": cached.pb_ratio,
                "market_cap": cached.market_cap,
                "timestamp": cached.timestamp,
                "source": "cache"
            }
    
        spot_dict = get_stock_spot_dc(symbol)
        spot = StockSpot(
                        symbol=symbol,
                        market=market,
                        name=spot_dict['名称'] if '名称' in spot_dict else "",
                        current_price=float(spot_dict['现价']) if '现价' in spot_dict else 0.0,
                        open_price=float(spot_dict['开盘']) if '开盘' in spot_dict else 0.0,
                        high_price=float(spot_dict['最高']) if '最高' in spot_dict else 0.0,
                        low_price=float(spot_dict['最低']) if '最低' in spot_dict else 0.0,
                        pe_ratio=float(spot_dict['市盈率-TTM']) if '市盈率-TTM' in spot_dict else 0.0,
                        pb_ratio=float(spot_dict['市净率']) if '市净率' in spot_dict else 0.0,
                        market_cap=float(spot_dict['总市值']) if '总市值' in spot_dict else 0.0,
                        timestamp=datetime.now()
        )
        existing_spot = db.query(StockSpot).filter(
            StockSpot.symbol == symbol,
            StockSpot.market == market
        ).first()
        if existing_spot:
            db.query(StockSpot).filter(
                StockSpot.symbol == symbol,
                StockSpot.market == market
            ).update({
                StockSpot.name: spot.name,
                StockSpot.current_price: spot.current_price,
                StockSpot.open_price: spot.open_price,
                StockSpot.high_price: spot.high_price,
                StockSpot.low_price: spot.low_price,
                StockSpot.pe_ratio: spot.pe_ratio,
                StockSpot.pb_ratio: spot.pb_ratio,
                StockSpot.market_cap: spot.market_cap,
                StockSpot.timestamp: spot.timestamp
            })
        else:
            db.add(spot)
        db.commit()
        return {
            "symbol": spot.symbol,
            "market": spot.market,
            "name": spot.name,
            "current_price": spot.current_price,
            "open_price": spot.open_price,
            "high_price": spot.high_price,
            "low_price": spot.low_price,
            "pe_ratio": spot.pe_ratio,
            "pb_ratio": spot.pb_ratio,
            "market_cap": spot.market_cap,
            "timestamp": spot.timestamp,
            "source": "akshare"
        }

def get_stock_history(
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = "daily",
    adjust: str = "",
    market: str = "SH"
):
    """
    Get historical stock data
    
    Args:
        symbol (str): The stock symbol
        start_date (str): Start date in format YYYYMMDD
        end_date (str): End date in format YYYYMMDD
        period (str, optional): Data frequency. Defaults to "daily"
        adjust (str, optional): Price adjustment type. Defaults to ""
        market (str, optional): The market of the stock. Defaults to "SH"
    """
    symbol_f, market = normalize_symbol(symbol)
    symbol = get_symbol_base(symbol_f)
    with SessionLocal() as db:    
        # Calculate expected working days
        expected_days = get_working_days(start_date, end_date)

        # Check cache first
        cached = db.query(StockHistory).filter(
            StockHistory.symbol == symbol,
            StockHistory.market == market,
            StockHistory.date >= datetime.strptime(start_date, "%Y%m%d"),
            StockHistory.date <= datetime.strptime(end_date, "%Y%m%d")
        ).all()
        
        if cached and len(cached) == expected_days:
            return [{
                "symbol": history.symbol,
                "market": history.market,
                "date": history.date,
                "open": history.open_price,
                "close": history.close_price,
                "high": history.high_price,
                "low": history.low_price,
                "volume": history.volume,
                "source": "cache"
            } for history in cached]
        
        logger.info(f"Fetched {start_date} to {end_date} from AKShare for symbol {symbol}")

        # Fetch from AKShare
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust
        )
        
        logger.info(f"Fetched {len(df)} rows from AKShare for symbol {symbol}")

        # Store in cache
        histories = []
        if "日期" not in df.columns:
            raise KeyError("The '日期' column is missing in the DataFrame. Please check the data source.")
        
        for _, row in df.iterrows():
            history = StockHistory(
                symbol=symbol,
                market=market,
                date=pd.to_datetime(row["日期"]),
                open_price=float(row["开盘"]),
                close_price=float(row["收盘"]),
                high_price=float(row["最高"]),
                low_price=float(row["最低"]),
                volume=float(row["成交量"])
            )
            histories.append(db.merge(history))
        
        db.commit()
        
        return [{
            "symbol": history.symbol,
            "market": history.market,
            "date": history.date,
            "open": history.open_price,
            "close": history.close_price,
            "high": history.high_price,
            "low": history.low_price,
            "volume": history.volume,
            "source": "akshare"
        } for history in histories]
