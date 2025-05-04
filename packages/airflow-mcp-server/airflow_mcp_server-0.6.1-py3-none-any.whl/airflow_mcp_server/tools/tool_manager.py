import logging

from mcp.types import Tool
from packaging.version import parse as parse_version

from airflow_mcp_server.client.airflow_client import AirflowClient
from airflow_mcp_server.config import AirflowConfig
from airflow_mcp_server.parser.operation_parser import OperationParser
from airflow_mcp_server.tools.airflow_tool import AirflowTool

logger = logging.getLogger(__name__)

_tools_cache: dict[str, AirflowTool] = {}


async def _initialize_tools(config: AirflowConfig) -> None:
    """Initialize tools cache with Airflow operations (async)."""
    global _tools_cache
    try:
        async with AirflowClient(base_url=config.base_url, auth_token=config.auth_token) as client:
            parser = OperationParser(client.raw_spec)
            for operation_id in parser.get_operations():
                operation_details = parser.parse_operation(operation_id)
                tool = AirflowTool(operation_details, client)
                _tools_cache[operation_id] = tool

    except Exception as e:
        logger.error("Failed to initialize tools: %s", e)
        _tools_cache.clear()
        raise ValueError(f"Failed to initialize tools: {e}") from e


async def get_airflow_tools(config: AirflowConfig, mode: str = "unsafe") -> list[Tool]:
    """Get list of available Airflow tools based on mode.

    Args:
        config: Configuration object with auth and URL settings
        mode: "safe" for GET operations only, "unsafe" for all operations (default)

    Returns:
        List of MCP Tool objects representing available operations

    Raises:
        ValueError: If initialization fails
    """

    # Version check before returning tools
    if not _tools_cache:
        await _initialize_tools(config)

    # Only check version if get_version tool is present
    if "get_version" in _tools_cache:
        version_tool = _tools_cache["get_version"]
        async with version_tool.client:
            version_result = await version_tool.run()
        airflow_version = version_result.get("version")
        if airflow_version is None:
            raise RuntimeError("Could not determine Airflow version from get_version tool.")
        if parse_version(airflow_version) < parse_version("3.1.0"):
            raise RuntimeError(f"Airflow version {airflow_version} is not supported. Requires >= 3.1.0.")

    tools = []
    for operation_id, tool in _tools_cache.items():
        try:
            # Skip non-GET operations in safe mode
            if mode == "safe" and not tool.operation.method.lower() == "get":
                continue
            schema = tool.operation.input_model.model_json_schema()
            tools.append(
                Tool(
                    name=operation_id,
                    description=tool.operation.description,
                    inputSchema=schema,
                )
            )
        except Exception as e:
            logger.error("Failed to create tool schema for %s: %s", operation_id, e)
            continue

    return tools


async def get_tool(config: AirflowConfig, name: str) -> AirflowTool:
    """Get specific tool by name.

    Args:
        config: Configuration object with auth and URL settings
        name: Tool/operation name

    Returns:
        AirflowTool instance

    Raises:
        KeyError: If tool not found
        ValueError: If tool initialization fails
    """
    if not _tools_cache:
        await _initialize_tools(config)

    if name not in _tools_cache:
        raise KeyError(f"Tool {name} not found")

    return _tools_cache[name]
