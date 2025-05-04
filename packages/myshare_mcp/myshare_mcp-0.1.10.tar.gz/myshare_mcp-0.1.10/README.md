# MyShare MCP

Financial data analysis assistant based on AKShare with local SQLite caching.

## Setup

1. Create and activate virtual environment:
   
   ```bash
   uv add "mcp[cli]"
   uv init myshare-mcp
   cd myshare-mcp
   uv venv
   .venv/Scripts/activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   
   ```bash
   pip install -e .
   ```

## API and MCP Endpoints

## Testing MCP

To test mcp, please use the following command:

```powershell
C:\>myshare-mcp>uv run mcp

 Usage: mcp [OPTIONS] COMMAND [ARGS]...

 MCP development tools

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ version   Show the MCP version.                                                                                   │
│ dev       Run a MCP server with the MCP Inspector.                                                                │
│ run       Run a MCP server.                                                                                       │
│ install   Install a MCP server in the Claude desktop app.                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

To debug using MCP inspector:

```powershell
C:\>myshare-mcp>uv run mcp dev main.py
Starting MCP inspector...
⚙️ Proxy server listening on port 6277
New SSE connection
Query parameters: [Object: null prototype] {
  transportType: 'stdio',
  command: 'uv',
  args: 'run --with mcp mcp run main.py',
...
```

## Testing FastAPI

```powershell
C:\>myshare-mcp>uv run main.py
```

## API implementation

### 1. Real-time Stock Data

```http
GET /spot/{symbol}
```

Gets real-time stock data for a given symbol (e.g., "SH600000").

Example response:

```json
{
    "symbol": "SH600000",
    "name": "浦发银行",
    "current_price": 7.21,
    "open_price": 7.19,
    "high_price": 7.25,
    "low_price": 7.18,
    "pe_ratio": 4.85,
    "pb_ratio": 0.41,
    "market_cap": 211731000000,
    "timestamp": "2025-04-26T10:30:00",
    "source": "akshare"
}
```

### 2. Historical Stock Data

```http
GET /history/{symbol}?start_date={YYYYMMDD}&end_date={YYYYMMDD}&period={daily|weekly|monthly}&adjust={qfq|hfq}
```

Gets historical stock data for a given symbol and date range.

Parameters:

- start_date: Start date in YYYYMMDD format
- end_date: End date in YYYYMMDD format
- period: Data frequency (daily, weekly, monthly)
- adjust: Price adjustment (qfq for forward-adjusted, hfq for backward-adjusted)

Example response:

```json
[
    {
        "date": "2025-04-26T00:00:00",
        "open": 7.19,
        "close": 7.21,
        "high": 7.25,
        "low": 7.18,
        "volume": 123456,
        "source": "akshare"
    }
]
```

## Caching

All data is automatically cached in a local SQLite database (finance.db). The cache is checked before making requests to AKShare.

## Symbol

The following table is the format of stock symbol for different markets.
Please refer to `symbol.md`.

## Database

We can use sqlite_web to navigate the database.

[coleifer/sqlite-web: Web-based SQLite database browser written in Python](https://github.com/coleifer/sqlite-web)

```powershell
sqlite_web .\finance.db
```