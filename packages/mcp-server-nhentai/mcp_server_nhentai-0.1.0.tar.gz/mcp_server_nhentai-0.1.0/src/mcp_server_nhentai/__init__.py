from .server import serve


def main():
    """MCP nhentai Server - nhentai for MCP"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()