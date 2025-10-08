"""MCP stdio server with lifespan-provided auth context.

This example shows how to:
- Configure process logging
- Use FastMCP lifespan to perform startup-time validation (simple email allowlist)
- Expose a tool (`whoami`) that reads values from the lifespan context

Clients should spawn this process with an `email` environment variable. The
value is validated against a small allowlist during startup.
"""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

from llm_cookbook.utils.logger_config import base_log_config

# Setup logger for this module
logging.config.dictConfig(base_log_config)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Minimal allowlist for demonstration purposes only. Replace with real auth.
ALLOW_EMAILS = {"test@test.com", "test2@test.dev"}


@dataclass
class AuthContext:
    email: str


async def verify_email(email: str) -> str:
    """Validate the provided email against the allowlist.

    Returns the email if valid; raises RuntimeError otherwise.
    """
    logger.info(f"Verifying email: {email}")
    # Replace with a real verification (e.g., call an auth service)
    if email in ALLOW_EMAILS:
        return email
    raise RuntimeError("Invalid email address")


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AuthContext]:
    """Create and yield an `AuthContext` for each server lifetime.

    Reads `email` from the environment, validates it, and exposes the result
    to tools via `ctx.request_context.lifespan_context`.
    """
    request_email = os.environ.get("email", None)
    logging.info(f"Request email: {request_email}")

    # Perform authentication/validation
    email = await verify_email(request_email)  # raise if invalid

    yield AuthContext(email=email)


mcp = FastMCP(name="Auth Server", lifespan=lifespan)


@mcp.tool()
def whoami(ctx: Context) -> dict:
    """Return the authenticated identity from lifespan context."""
    auth: AuthContext = ctx.request_context.lifespan_context
    return {"email": auth.email}


if __name__ == "__main__":
    # Run in stdio; clients spawn this process with env
    mcp.run(transport="stdio")
