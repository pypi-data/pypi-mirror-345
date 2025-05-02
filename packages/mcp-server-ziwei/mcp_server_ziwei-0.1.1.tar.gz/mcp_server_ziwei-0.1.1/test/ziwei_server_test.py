import asyncio
import sys
import os

# 加入 src 到 sys.path，確保能找到 mcp_server_ziwei
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from mcp_server_ziwei.server import (
    ZiweiInput,
    extract_ziwei_main_section,
    call_tool,
    TextContent,
    McpError,
)


async def test_call_ziwei_tool_success():
    print("🧪 Running test_call_ziwei_tool_success...")

    class MockResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, *args, **kwargs):
            return MockResponse("""
                <font color=blue>本命：命宮</font>
                <table><tr><td>命盤資料</td></tr></table>
                <br>
                <center><form><input type=button value="回上頁"></form></center>
            """)

    import mcp_server_ziwei.server as server
    server.httpx.AsyncClient = lambda: MockClient()  # monkey patch

    args = {
        "Sex": 1,
        "Year": 1990,
        "Month": 1,
        "Day": 1,
        "Hour": 12,
        "Solar": 1,
        "Leap": 0
    }

    result = await call_tool("get_ming_pan", args)
    assert isinstance(result, list)
    assert any("<table>" in content.text for content in result if isinstance(content, TextContent))
    print("✅ Passed.")


async def test_call_ziwei_tool_missing_required():
    print("🧪 Running test_call_ziwei_tool_missing_required...")
    args = {
        "Year": 1990,
        "Month": 1,
        "Day": 1,
        "Hour": 12
    }

    try:
        await call_tool("get_ming_pan", args)
    except McpError as e:
        assert "Sex" in str(e)
        print("✅ Passed.")
    else:
        raise Exception("❌ test_call_ziwei_tool_missing_required failed: No exception raised")


async def test_call_ziwei_tool_external_api_fail():
    print("🧪 Running test_call_ziwei_tool_external_api_fail...")

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, *args, **kwargs):
            raise Exception("mock network error")

    import mcp_server_ziwei.server as server
    server.httpx.AsyncClient = lambda: MockClient()

    args = {
        "Sex": 1,
        "Year": 1990,
        "Month": 1,
        "Day": 1,
        "Hour": 12,
    }

    try:
        await call_tool("get_ming_pan", args)
    except McpError as e:
        assert "外部 API 請求錯誤" in str(e)
        print("✅ Passed.")
    else:
        raise Exception("❌ test_call_ziwei_tool_external_api_fail failed: No exception raised")


def test_extract_ziwei_main_section_success():
    print("🧪 Running test_extract_ziwei_main_section_success...")

    html = """
        <font color=blue>本命：命宮</font>
        <table><tr><td>測試命盤</td></tr></table>
        <br>
        <center><form><input type=button value="回上頁"></form></center>
    """
    result = extract_ziwei_main_section(html)
    assert "<table>" in result
    assert "測試命盤" in result
    print("✅ Passed.")


def test_extract_ziwei_main_section_missing_start():
    print("🧪 Running test_extract_ziwei_main_section_missing_start...")

    html = "<html><body>no start marker</body></html>"
    result = extract_ziwei_main_section(html)
    assert "找不到起始標記" in result
    print("✅ Passed.")


def test_extract_ziwei_main_section_missing_end():
    print("🧪 Running test_extract_ziwei_main_section_missing_end...")

    html = "<font color=blue>本命：命宮</font><table><tr><td>命盤</td></tr></table>"
    result = extract_ziwei_main_section(html)
    assert "找不到結束標記" in result
    print("✅ Passed.")


async def main():
    await test_call_ziwei_tool_success()
    await test_call_ziwei_tool_missing_required()
    await test_call_ziwei_tool_external_api_fail()
    test_extract_ziwei_main_section_success()
    test_extract_ziwei_main_section_missing_start()
    test_extract_ziwei_main_section_missing_end()


if __name__ == "__main__":
    asyncio.run(main())
