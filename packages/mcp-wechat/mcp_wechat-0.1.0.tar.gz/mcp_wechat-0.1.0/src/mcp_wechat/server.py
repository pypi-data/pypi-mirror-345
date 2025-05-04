import argparse
from typing import Any
from mcp.server.fastmcp import FastMCP
import mcp.server
import wxauto
from wxauto import WeChat

wx = WeChat()

# 初始化 MCP 服务器
mcp = FastMCP(name="wechat",port=8001)


# @mcp.tool()
# async def query_weather(city: str) -> str:
#     """输入指定城市的英文名称，返回今日天气查询结果。"""
#     data = await fetch_weather(city)
#     return format_weather(data)
@mcp.tool()
def send_text(text:str,nick_name:str):
    '''发送文本信息给指定的昵称的群或者个人'''
    wx.SendMsg(text,nick_name)
    return "ok"

@mcp.tool()
def send_files(files_path:str|list,nick_name:str):
    '''发送文件(包含图片等文件)给指定的群或者个人'''
    wx.SendFiles(files_path,nick_name)
    return "ok"

def main():
    # parser = argparse.ArgumentParser(description="WeChat Server")
    # parser.add_argument("--api_key", type=str, required=True, help="你的OpenWeather API Key")
    # args = parser.parse_args()
    # global API_KEY
    # API_KEY = args.api_key
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
