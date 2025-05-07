
import json
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import anyio
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
# Webull Pay SDK
from webullpaysdkcore.client import ApiClient
from webullpaysdkmdata.common.category import Category
from webullpaysdktrade.api import API as WBAPI


# ---------- 1) 生命周期 ----------
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """服务器启动 / 关闭时执行一次"""
    client = ApiClient(
        app_key= os.getenv("WEBULL_APP_KEY", "4008e8b89edadd22eb5abcf1fb6851e683c9698142442f2bfcc2acb24037449d"),
        app_secret= os.getenv("WEBULL_APP_SECRET","6c65d9bfa9a51ccd7a0cf39cc4833cf4f8c932ab1bf109eb77b69512f51c9c25"),
        region_id="us"
    )
    endpoint = os.getenv("WEBULL_ENDPOINT",
                         "u1spay-openapi.pre.webullbroker.com")

    client._endpoint_resolver.put_endpoint_entry(
        region_id="us",
        api_type="api",
        endpoint=endpoint  # 你的自定义域名
    )

    api = WBAPI(client)
    try:
        yield {"api": api}          # ctx.request_context.lifespan_context["api"]
    finally:
        await anyio.to_thread.run_sync(client.close)  # SDK 里如果有 close()


# # 初始化 FastMCP 服务器
mcp =  FastMCP(
    "webullpay",
    description="Webull Pay OpenAPI 的 MCP 封装",
    lifespan=app_lifespan
)



# ---------- 工具 1：最新报价 ----------
@mcp.tool(description="""
获取加密货币的实时行情。示例：
get_snapshot({ "symbols": "BTCUSD" })
返回格式：// list返回的,格式如下,
[
    {
        "symbol": "BTCUSD",
        "open": "94224.9900000000", // 开盘价
        "high": "94391.9500000000", // 最高价
        "low": "93677.5750000000", // 最低价
        "pre_close": "94224.5600000000", //昨日关盘价
        "change": "-184.3550000000", // 当前价格对比开盘价的浮动
        "change_ratio": "-0.0019565493", //当前价格对比开盘价的浮动比例
        "instrument_id": "950160802", // 标的档案ID
        "trade_timestamp": 1745763071474 // 价格时间
    }
]
""")
def get_quote(symbols: str, ctx: Context):
    api: WBAPI = ctx.request_context.lifespan_context["api"]
    return json.dumps(api.market_data.get_snapshot(symbols=symbols,
                                     category=Category.CRYPTO.name).json(), ensure_ascii=False)


@mcp.tool(description="""获取指定 Webull Pay 账户的余额信息
返回格式：
{
    "account_id": "co393b0ab01", // 账号
    "currency": "USD", // 币种
    "total_amount": "999", // 总余额
    "cash_balance": "967.58", // 现金余额
    "purchasing_amount": "966.58", // 可购买余额
    "available_amount": "956.57", // 可出金余额
    "total_market_value": "2807.15", // 持仓总市值
    "total_value": "3774.73" // 现金+持仓市值的总值
}
""")
def get_balance(account_id: str, ctx: Context):
    api: WBAPI = ctx.request_context.lifespan_context["api"]
    return json.dumps(api.account.get_account_balance(account_id=account_id).json(), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport='stdio')