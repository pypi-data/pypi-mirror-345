from enum import Enum
import json
from typing import Sequence
import httpx

from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, EmbeddedResource, ImageContent
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS


class ZiweiTools(str, Enum):
    GET_MING_PAN = "get_ming_pan"


class ZiweiInput(BaseModel):
    Sex: int = Field(description="性別 (1: 男, 0: 女)", ge=0, le=1)
    Year: int = Field(description="出生年 (西元)", ge=1, le=3400)
    Month: int = Field(description="出生月", ge=1, le=12)
    Day: int = Field(description="出生日", ge=1, le=31)
    Hour: int = Field(description="出生時 (0-23 小時制)", ge=0, le=23)
    Solar: int = Field(default=1, description="曆法 (1: 國曆, 0: 農曆)；預設為國曆")
    Leap: int = Field(default=0, description="是否閏月；若為國曆固定為 0，農曆才需要根據情況設定")


def extract_ziwei_main_section(html: str) -> str:
    start_marker = '<font color=blue>本命：命宮</font>'
    end_marker = '</td></tr></table>\n<br>\n<center><form><input type=button value="回上頁"'

    start_index = html.find(start_marker)
    if start_index == -1:
        return "<error>找不到起始標記：<font color=blue>本命：命宮</font></error>"

    end_index = html.find(end_marker)
    if end_index == -1:
        return "<error>找不到結束標記：回上頁按鈕前的 </table></error>"

    end_of_table_index = html[:end_index].rfind('</table>')
    if end_of_table_index == -1:
        return "<error>找不到對應的 </table> 標籤</error>"

    main_str = html[start_index:end_of_table_index + len('</table>')]

    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>紫微命盤</title>
</head>
<body>
{main_str}
</body>
</html>
"""

    return full_html + "\n\n**請寫成HTML程式**\n**請勿修改任何 table 的排版與內容**"


async def serve() -> None:
    server = Server("mcp-ziwei")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=ZiweiTools.GET_MING_PAN.value,
                description="計算紫微斗數命盤。使用者需提供性別、出生年月日與時辰，若未提供曆法則預設為國曆。",
                inputSchema=ZiweiInput.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if name != ZiweiTools.GET_MING_PAN.value:
            raise ValueError(f"未知工具名稱: {name}")

        try:
            args = ZiweiInput(**arguments)
        except Exception as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        # Leap 邏輯處理
        solar = args.Solar if args.Solar is not None else 1
        leap = args.Leap if solar == 0 else 0

        payload = {
            "FUNC": "Basic",
            "Target": "0",
            "SubTarget": "-1",
            "Sex": str(args.Sex),
            "Solar": str(solar),
            "Leap": str(leap),
            "Year": str(args.Year),
            "Month": str(args.Month),
            "Day": str(args.Day),
            "Hour": str(args.Hour),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://fate.windada.com/cgi-bin/fate",
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30,
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"外部 API 請求錯誤：{str(e)}"))

        html_result = extract_ziwei_main_section(response.text)

        return [TextContent(type="text", text=html_result)]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)