
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters

from meshagent.mcp import MCPToolkit

from meshagent.cli import async_typer
import typer
from meshagent.cli.helper import get_client, print_json_table, set_active_project, resolve_project_id
from rich import print
from meshagent.api import RoomClient, ParticipantToken, WebSocketClientProtocol, RoomException
from meshagent.cli.helper import set_active_project, get_active_project, resolve_project_id, resolve_api_key
from typing import Annotated, Optional
from meshagent.api.helpers import meshagent_base_url, websocket_room_url

from meshagent.api.services import send_webhook
from meshagent.tools.hosting import RemoteToolkit
import shlex

app = async_typer.AsyncTyper()

@app.async_command("sse")
async def sse(*, project_id: str = None, room: Annotated[str, typer.Option()], api_key_id: Annotated[Optional[str], typer.Option()] = None, name: Annotated[str, typer.Option(..., help="Participant name")] = "cli", role: str = "tool", url: Annotated[str, typer.Option()]):
    account_client = await get_client()
    try:
        project_id = await resolve_project_id(project_id=project_id)
        api_key_id = await resolve_api_key(project_id, api_key_id)

        key = (await account_client.decrypt_project_api_key(project_id=project_id, id=api_key_id))["token"]

        token = ParticipantToken(
            name=name,
            project_id=project_id,
            api_key_id=api_key_id
        )

        token.add_role_grant(role=role)
        token.add_room_grant(room)

        print("[bold green]Connecting to room...[/bold green]")
        async with RoomClient(protocol=WebSocketClientProtocol(url=websocket_room_url(room_name=room, base_url=meshagent_base_url()), token=token.to_jwt(token=key))) as client:
            
            async with sse_client(url) as (read_stream, write_stream):

                async with ClientSession(read_stream=read_stream, write_stream=write_stream) as session:
                    
                    mcp_tools_response = await session.list_tools()
                    
                    toolkit = MCPToolkit(name=name, session=session, tools=mcp_tools_response.tools)
                    
                    remote_toolkit = RemoteToolkit(name=toolkit.name, tools=toolkit.tools, title=toolkit.title, description=toolkit.description)

                    await remote_toolkit.start(room=client)
                    try:
                        await client.protocol.wait_for_close()
                    except KeyboardInterrupt:
                        await remote_toolkit.stop()


    except RoomException as e:
        print(f"[red]{e}[/red]")
    finally:
        await account_client.close()



@app.async_command("stdio")
async def stdio(*, project_id: str = None, room: Annotated[str, typer.Option()], api_key_id: Annotated[Optional[str], typer.Option()] = None, name: Annotated[str, typer.Option(..., help="Participant name")] = "cli", role: str = "tool", command: Annotated[str, typer.Option()], args: Annotated[str, typer.Option()]):
    account_client = await get_client()
    try:
        project_id = await resolve_project_id(project_id=project_id)
        api_key_id = await resolve_api_key(project_id, api_key_id)

        key = (await account_client.decrypt_project_api_key(project_id=project_id, id=api_key_id))["token"]

        token = ParticipantToken(
            name=name,
            project_id=project_id,
            api_key_id=api_key_id
        )

        token.add_role_grant(role=role)
        token.add_room_grant(room)

        print("[bold green]Connecting to room...[/bold green]")
        async with RoomClient(protocol=WebSocketClientProtocol(url=websocket_room_url(room_name=room, base_url=meshagent_base_url()), token=token.to_jwt(token=key))) as client:
            
            async with stdio_client(StdioServerParameters(
                    command=command,  # Executable
                    args=shlex.split(args),  # Optional command line arguments
                    env=None,  # Optional environment variables
                )) as (read_stream, write_stream):

                async with ClientSession(read_stream=read_stream, write_stream=write_stream) as session:
                    
                    mcp_tools_response = await session.list_tools()
                    
                    toolkit = MCPToolkit(name=name, session=session, tools=mcp_tools_response.tools)
                    
                    remote_toolkit = RemoteToolkit(name=toolkit.name, tools=toolkit.tools, title=toolkit.title, description=toolkit.description)

                    await remote_toolkit.start(room=client)
                    try:
                        await client.protocol.wait_for_close()
                    except KeyboardInterrupt:
                        await remote_toolkit.stop()


    except RoomException as e:
        print(f"[red]{e}[/red]")
    finally:
        await account_client.close()
