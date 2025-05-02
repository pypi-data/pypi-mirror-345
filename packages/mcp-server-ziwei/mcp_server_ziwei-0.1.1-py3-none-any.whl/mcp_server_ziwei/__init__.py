from .server import serve


def main():
    """MCP Ziwei Server - Ziwei for MCP"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()