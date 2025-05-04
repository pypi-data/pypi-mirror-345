import logging
from fastapi import FastAPI, HTTPException
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import FastMCPError
from myshare_mcp.myshare.utils import setup_logger
from myshare_mcp.myshare.data import get_stock_spot, get_stock_history

# Initialize logger
setup_logger()
logger = logging.getLogger(__name__)

# Example usage
logger.info("AKShare MCP server starting...")

# Create an MCP server
mcp = FastMCP("Demo")

# Initialize FastAPI app
app = FastAPI(title="MyShare MCP Server")
                
@mcp.tool()
def mcp_get_stock_spot(symbol: str) -> Dict[str, Any]:
    """Get real-time stock data"""
    try:
        return get_stock_spot(symbol)
    except Exception as e:
        raise FastMCPError(f"Error fetching stock data for symbol '{symbol}': {e}")

@app.get("/spot/{symbol}")
async def web_get_stock_spot(symbol: str):
    """Get real-time stock data"""
    try:
        return get_stock_spot(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data for symbol '{symbol}': {e}")


@mcp.tool()
def mcp_get_stock_history(
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = "daily",
    adjust: str = ""
) -> Dict[str, Any]:
    """Get historical stock data"""
    try:
        return get_stock_history(symbol, start_date, end_date, period, adjust)
    except Exception as e:
        raise FastMCPError(f"Error fetching stock history for symbol '{symbol}': {e}")
            
@app.get("/history/{symbol}")
async def web_get_stock_history(
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = "daily",
    adjust: str = ""
):
    """Get historical stock data"""
    try:
        return get_stock_history(symbol, start_date, end_date, period, adjust)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock history for symbol '{symbol}': {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
