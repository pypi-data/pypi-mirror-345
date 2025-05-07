from mcp.server.fastmcp import FastMCP
import click
import logging

from alibaba_cloud_ops_mcp_server.config import config
from alibaba_cloud_ops_mcp_server.tools import cms_tools, oos_tools, oss_tools, api_tools

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(transport: str):
    # Create an MCP server
    mcp = FastMCP("alibaba-cloud-ops-mcp-server")
    for tool in oos_tools.tools:
        mcp.add_tool(tool)
    for tool in cms_tools.tools:
        mcp.add_tool(tool)
    for tool in oss_tools.tools:
        mcp.add_tool(tool)
    api_tools.create_api_tools(mcp, config)

    # Initialize and run the server
    logger.debug(f'mcp server is running on {transport} mode.')
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
