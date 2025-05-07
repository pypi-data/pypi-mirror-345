import argparse
from trade_mcp.server.mcp_tools import setup_mcp_tools
from trade_mcp.api.client import APIClientManager

def main():
    """Main entry point for the trading MCP server.
    
    Run with:
        python -m trade_mcp.server.main --api-key YOUR_KEY --api-secret YOUR_SECRET --provider aster
    """
    parser = argparse.ArgumentParser(description='Run Trading MCP server')
    parser.add_argument('--axgrad-key', required=True, help='API key for the trading platform')
    args = parser.parse_args()

    # Initialize API client
    APIClientManager.initialize(
        axgrad_key=args.axgrad_key,
    )

    # Set up and run MCP server
    mcp = setup_mcp_tools()
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main() 