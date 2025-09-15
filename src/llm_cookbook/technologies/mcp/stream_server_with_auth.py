"""Minimal FastMCP streamable HTTP server with authentication examples.

This script demonstrates how to start a FastMCP server using either:

- Static token verification for development/testing
- JWT verification for more realistic auth flows
- Customized JWT verification for more realistic auth flows

Usage:
    Run this module directly to start a development server:
        $ uv run python -m llm_cookbook.technologies.mcp.stream_server_with_auth

Access configuration:
{
    "mcpServers": {
        "local-mcp-server": {
            "url": "http://127.0.0.1:4200/stream-auth",
            "headers": {
                "Authorization": "Bearer <your-token>"
            }
        }
    }
}

Auth notes:
- Static tokens are useful during development to quickly test auth + scopes.
- For JWT, ensure the provided secret/public key and algorithm match how your
  tokens are signed. You can generate tokens at `https://jwt.io` for testing.

References:
- Token verification docs: `https://gofastmcp.com/servers/auth/token-verification`
"""

import logging

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.dependencies import AccessToken, get_access_token

from llm_cookbook.utils.logger_config import base_log_config

# Setup logger for this module
logging.config.dictConfig(base_log_config)

logger = logging.getLogger(__name__)


# Define development tokens and their associated claims (scopes).
# In development, embed static tokens in your client requests as a Bearer token.
static_verifier = StaticTokenVerifier(
    tokens={
        "dev-alice-token": {
            "client_id": "alice@company.com",
            "scopes": ["read:data", "write:data", "admin:users"],
        },
        "dev-guest-token": {
            "client_id": "guest-user",
            "scopes": ["read:data"],
        },
    },
    required_scopes=["read:data"],
)

# JWT verifier configuration
# - Generate a JWT (e.g., at https://jwt.io) using the same secret/key + algorithm.
# - Send it as an Authorization Bearer token in client requests.
jwt_verifier = JWTVerifier(
    # Same secret/key used to sign the JWT; keep secrets out of source control.
    public_key="a-string-secret-at-least-256-bits-long",
    algorithm="HS256",
    # Optional: enforce claims if you include them in the token
    issuer="localhost",
)


# Customized JWT verifier
class CustomizedJWTVerifier(JWTVerifier):
    async def verify_token(self, token: str):
        access = await super().verify_token(token)
        logger.info(f"Verified access: {access}")
        # access = None means the token is invalid
        if access is not None:
            logger.info(f"Verified token: {token}")
            logger.info(f"Verified token with claims: {access.claims}")
            # MCP context cannot be updated here, sadly.
        return access


customized_jwt_verifier = CustomizedJWTVerifier(
    public_key="a-string-secret-at-least-256-bits-long",
    algorithm="HS256",
    issuer="localhost",
)

mcp = FastMCP(
    name="Development Server",
    # Choose your verifier: `jwt_verifier` (default here) or `static_verifier` or `customized_jwt_verifier`
    auth=jwt_verifier,
)


@mcp.tool
async def whoami() -> dict:
    # Get the access token from the provided function
    token: AccessToken | None = get_access_token()

    logging.info(f"Token: {token}")
    if token is None:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "client_id": token.client_id,
        "scopes": token.scopes,
        "expires_at": token.expires_at,
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=4200,
        path="/stream-auth",
        log_level="INFO",
    )
