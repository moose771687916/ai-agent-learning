# ============================================================
# day10/mcp_server.py - 第一个MCP服务器
# ============================================================

from mcp.server.mcpserver import MCPServer
import requests

# 创建MCP服务器
mcp = MCPServer("macro-eco-tools")

# 加工具：查汇率
@mcp.tool()
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """查汇率，比如美元兑人民币、欧元兑美元"""
    import requests
    try:
        # 用新浪财经的汇率API
        url = f"https://hq.sinajs.cn/list=fx_s{base_currency.lower()}{target_currency.lower()}"
        headers = {"Referer": "https://finance.sina.com.cn"}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.text.split("=")[1].split(",")
        if len(data) > 1:
            rate = data[1]
            return f"1 {base_currency} = {rate} {target_currency}"
        else:
            return f"找不到 {base_currency} 兑 {target_currency} 的汇率"
    except Exception as e:
        return f"查询汇率失败：{str(e)}"


# 加工具：查股票指数
@mcp.tool()
def get_stock_index(index_name: str) -> str:
    """查股票指数，比如上证指数、纳斯达克指数"""
    try:
        # 用免费的API查
        url = f"https://api.stock-api.com/v1/index/{index_name}"
        res = requests.get(url, timeout=5)
        data = res.json()
        return f"{index_name}：{data.get('price', '未知')} 点"
    except Exception as e:
        return f"查询股票指数失败：{str(e)}"


# 启动MCP服务器
if __name__ == "__main__":
    mcp.run()
