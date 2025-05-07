from .mcp_mysql_connect import mcp
import logging

def main():
    logging.info("Starting MCP server...")
    try:
        logging.info("Server is ready to accept connections on default port...")
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested...")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")

__all__ = ['main', 'mcp'] 