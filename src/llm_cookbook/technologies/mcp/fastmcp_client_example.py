# math_client.py
import asyncio

from fastmcp import Client


async def main():
    async with Client("fastmcp_server_example.py") as client:
        while True:
            try:
                cmd = input("Enter command (add/multiply/exit): ").strip().lower()
                if cmd == "exit":
                    break

                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))

                result = await client.call_tool(cmd, {"a": a, "b": b})
                print(f"Result: {result[0].text}")

            except Exception as e:
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
