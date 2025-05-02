from typing import Union

from ambient_backend_api_client.models.node import Node
from ambient_event_bus_client.models.event_api_models import MessageCreate

from ambient_client_common import config
from ambient_client_common.repositories.base_api_repo import get, patch, post

url = config.settings.edge_server_url


async def get_node(headers: dict) -> Union[Node, None]:
    """Get node data from the local API."""
    node = await get(url + "/data/node", headers=headers)
    if node:
        return Node.model_validate(node)
    return None


async def refresh_node(headers: dict) -> Union[Node, None]:
    """Refresh node data from the local API."""
    node = await get(url + "/data/node/refresh", headers=headers)
    if node:
        return Node.model_validate(node)
    return None


async def patch_node(node_id: int, data: dict, headers: dict) -> Node:
    """Patch node data in the local API."""
    response = await patch(url + "/data/node", data=data, headers=headers)
    if response:
        return Node.model_validate(response)
    raise ValueError("Failed to patch node data")


async def publish_event(msg: MessageCreate, headers: dict) -> dict:
    """Publish an event to the local API."""
    response_data = await post(url + "/events", data=msg.model_dump(), headers=headers)
    return response_data


async def get_api_token(headers: dict) -> str:
    """Get the API token from the local API."""
    response = await get(url + "/auth/token", headers=headers)
    if response:
        return response.get("token")
    raise ValueError("Failed to get API token")
