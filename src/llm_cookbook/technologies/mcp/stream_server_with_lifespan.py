"""Minimal FastMCP streamable HTTP server with lifespan examples.

This script demonstrates how to start a FastMCP server using lifespan context.

Access configuration:
{
    "mcpServers": {
        "local-mcp-server": {
            "url": "http://127.0.0.1:4200/stream-lifespan",
            "headers": {
                "email": "test2@test.dev"
            }
        }
    }
}

Auth notes:
- The email is validated against a small allowlist added during startup.

"""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp import Context, FastMCP

from llm_cookbook.utils.logger_config import base_log_config

# Setup logger for this module
logging.config.dictConfig(base_log_config)

logger = logging.getLogger()

# Minimal allowlist for demonstration purposes only. Replace with real auth.
ALLOW_EMAILS = {"test@test.com", "test2@test.dev"}


@dataclass
class AppConfig:
    allowed_emails: set[str]


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppConfig]:
    ######## Startup code ########
    # Load server-side config at startup (not per-client env)
    allowed = os.environ.get("ALLOWED_EMAILS", ",".join(ALLOW_EMAILS))
    logger.info(f"Allowed emails: {allowed}")
    cfg = AppConfig(allowed_emails={e.strip() for e in allowed.split(",") if e.strip()})
    # Fail fast if misconfigured (example)
    if not cfg.allowed_emails:
        raise RuntimeError("No allowed emails configured")
    ######## Startup code ########
    yield cfg  # This can be accessed by the tools via ctx.request_context.lifespan_context
    ######## Shutdown code ########
    logger.info("Shutting down server")
    ######## Shutdown code ########


mcp = FastMCP(
    name="DevServerWithLifespan",
    lifespan=lifespan,
)


async def get_incoming_email(ctx: Context) -> str:
    # Prefer the underlying Starlette Request when using streamable HTTP
    req = ctx.request_context.request
    if req:
        # Accept either "email" or "x-email"
        return req.headers.get("email") or req.headers.get("x-email") or ""
    # Fallback: some adapters may inject into meta
    meta = ctx.request_context.meta or {}
    return meta.get("email") or meta.get("x-email") or ""


async def ensure_authenticated(ctx: Context) -> str:
    email = await get_incoming_email(ctx)
    email = email.strip().lower()
    cfg: AppConfig = ctx.request_context.lifespan_context
    if email not in cfg.allowed_emails:
        # Raising here blocks tool execution; clients receive a clear error
        raise RuntimeError(f"Unauthorized email: {email!r}")
    return email


@mcp.tool()
async def whoami(ctx: Context) -> dict:
    email = await ensure_authenticated(ctx)
    return {"email": email, "message": "authenticated"}


@mcp.tool()
async def secret_action(ctx: Context) -> str:
    email = await ensure_authenticated(ctx)
    return f"Top-secret action for {email}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=4200,
        path="/stream-lifespan",
        log_level="INFO",
    )
