"""Minimal FastMCP streamable HTTP server with middleware examples.

This script demonstrates how to start a FastMCP server using middleware.

ref:
https://gofastmcp.com/servers/context#state-management
"""

import logging

from fastmcp import Context, FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext

from llm_cookbook.utils.logger_config import base_log_config

# Setup logger for this module
logging.config.dictConfig(base_log_config)

logger = logging.getLogger(__name__)


class CustomHeaderMiddleware(Middleware):
    def _log_message_details(self, context: MiddlewareContext) -> None:
        """Log details about the MCP message."""
        if not (hasattr(context, "message") and context.message):
            return

        logger.info(f"Message object: {type(context.message).__name__}")

        # Log message attributes
        message_attrs = []
        for attr in dir(context.message):
            if not attr.startswith("_"):
                try:
                    value = getattr(context.message, attr)
                    if not callable(value):
                        message_attrs.append(f"{attr}: {value}")
                except Exception as e:
                    message_attrs.append(f"{attr}: <error getting value: {e}>")

        if message_attrs:
            logger.info("Message attributes:")
            for attr in message_attrs:
                logger.info(f"  {attr}")

    def _log_fastmcp_context(self, context: MiddlewareContext) -> None:
        """Log details about the FastMCP context."""
        if not (hasattr(context, "fastmcp_context") and context.fastmcp_context):
            logger.info("No FastMCP Context available")
            return

        logger.info(
            f"FastMCP Context available: {type(context.fastmcp_context).__name__}"
        )

        # Log FastMCP context attributes
        fastmcp_attrs = []
        for attr in dir(context.fastmcp_context):
            if not attr.startswith("_"):
                try:
                    value = getattr(context.fastmcp_context, attr)
                    if not callable(value):
                        fastmcp_attrs.append(f"{attr}: {value}")
                except Exception as e:
                    fastmcp_attrs.append(f"{attr}: <error getting value: {e}>")

        if fastmcp_attrs:
            logger.info("FastMCP Context attributes:")
            for attr in fastmcp_attrs:
                logger.info(f"  {attr}")

    def _log_additional_context(self, context: MiddlewareContext) -> None:
        """Log additional context attributes."""
        excluded_attrs = {
            "method",
            "source",
            "type",
            "timestamp",
            "message",
            "fastmcp_context",
        }

        # Log authentication context if available
        if hasattr(context, "auth_context"):
            logger.info(f"Auth Context: {context.auth_context}")

        # Log any additional context attributes
        context_attrs = []
        for attr in dir(context):
            if not attr.startswith("_") and attr not in excluded_attrs:
                try:
                    value = getattr(context, attr)
                    if not callable(value):
                        context_attrs.append(f"{attr}: {value}")
                except Exception as e:
                    context_attrs.append(f"{attr}: <error getting value: {e}>")

        if context_attrs:
            logger.info("Additional context attributes:")
            for attr in context_attrs:
                logger.info(f"  {attr}")

    def _log_result_details(self, result, context: MiddlewareContext) -> None:
        """Log details about the response result."""
        logger.info("=== Response Details ===")
        logger.info(f"Result type: {type(result).__name__}")

        # Log result attributes if available
        if result and hasattr(result, "__dict__"):
            result_attrs = []
            for attr, value in vars(result).items():
                if not attr.startswith("_"):
                    result_attrs.append(f"{attr}: {value}")

            if result_attrs:
                logger.info("Result attributes:")
                for attr in result_attrs:
                    logger.info(f"  {attr}")

    async def on_message(self, context: MiddlewareContext, call_next):
        # Log all available context information
        logger.info("=== MCP Middleware Context Details ===")
        logger.info(f"Method: {context.method}")
        logger.info(f"Source: {context.source}")
        logger.info(f"Type: {context.type}")
        logger.info(f"Timestamp: {context.timestamp}")

        self._log_message_details(context)
        self._log_fastmcp_context(context)
        self._log_additional_context(context)

        logger.info("=== Processing request ===")

        try:
            result = await call_next(context)
            self._log_result_details(result, context)
            logger.info(f"✅ Completed {context.method}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in {context.method}: {type(e).__name__}: {e}")
            logger.error("=== Error Context ===")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            raise

    # will be run before every tool call
    async def on_call_tool(self, context, call_next):
        # set the work mode to GO
        context.fastmcp_context.set_state("work_mode", "GO")
        return await call_next(context)


mcp = FastMCP(
    name="Development Server",
)


@mcp.tool
def multiply(a: float, b: float, context: Context) -> float:
    """Multiplies two numbers"""
    logger.info("running multiply tool")
    # Load the work mode from the context
    logger.info(f"context: {context.get_state('work_mode')}")
    return a * b


mcp.add_middleware(CustomHeaderMiddleware())

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=4200,
        path="/stream-middleware",
        log_level="INFO",
    )
