from .server import serve


def main():
    """MCP websearch Server - websearch for MCP"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()