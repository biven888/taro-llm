from fastmcp import Client


mcp_client = Client('http://localhost:9000/mcp')


async def call_tool(tool_name: str, arguments: dict):
    async with mcp_client:
        result = await mcp_client.call_tool(tool_name, arguments)
        result = result.content[0].text if result.content else 'Инструмент вернул пустой результат'
        return result
