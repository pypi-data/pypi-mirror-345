from meshagent.cli import async_typer
import typer
from meshagent.cli.helper import get_client, print_json_table, set_active_project, resolve_project_id
from rich import print
from meshagent.api import RoomClient, ParticipantToken
from meshagent.cli.helper import set_active_project, get_active_project, resolve_project_id
from typing import Annotated, Optional


app = async_typer.AsyncTyper()

@app.async_command("generate")
async def generate(*, project_id: str = None, room: Annotated[str, typer.Option()], api_key_id: Annotated[Optional[str], typer.Option()] = None, name: Annotated[str, typer.Option()], role: str = "agent"):
    client = await get_client()
    try:
        project_id = await resolve_project_id(project_id=project_id)

        key = (await client.decrypt_project_api_key(project_id=project_id, id=api_key_id))["token"]

        token = ParticipantToken(
            name=name,
            project_id=project_id,
            api_key_id=api_key_id
        )

        token.add_role_grant(role=role)

        token.add_room_grant(room)

        print(token.to_jwt(token=key))
    
    finally:
        await client.close()
