from typing import Union

from ambient_backend_api_client.models.cluster import Cluster
from ambient_backend_api_client.models.create_custer_request import CreateCusterRequest
from ambient_backend_api_client.models.node import Node

from ambient_client_common import config
from ambient_client_common.repositories.base_api_repo import get, patch, post
from ambient_client_common.utils import logger

url = config.settings.backend_api_url


async def decode_token(token: str) -> Union[dict, None]:
    """Decode the JWT token to get the user ID.

    Args:
        token (str): JWT token

    Returns:
        Union[dict, None]: Decoded token data or None if invalid
    """
    decoded = await post(
        f"{url}/oauth/decode", headers={"Authorization": f"Bearer {token}"}
    )
    if decoded:
        return decoded
    return None


async def get_node(node_id: int, headers: dict) -> Union[Node, None]:
    """Get node data from backend API.

    Args:
        node_id (int): node ID
        headers (dict): authentication headers

    Returns:
        Union[Node, None]: Node data or None if not found
    """
    node = await get(f"{url}/nodes/{node_id}", headers=headers)
    if node:
        return Node.model_validate(node)
    return None


async def patch_node(node_id: int, headers: dict, **values: dict) -> Union[Node, None]:
    """Patch node data in the backend API."""
    node = await patch(f"{url}/nodes/{node_id}", headers=headers, data=values)
    return Node.model_validate(node)


async def create_cluster(
    headers: dict, data: Union[dict, CreateCusterRequest]
) -> Union[Cluster, None]:
    """Create a cluster in the backend API."""
    if isinstance(data, CreateCusterRequest):
        data = data.model_dump(exclude_none=True)
    cluster = await post(f"{url}/clusters", headers=headers, data=data)
    if cluster:
        return Cluster.model_validate(cluster)
    return None


async def get_cluster(
    headers: dict, node_id: Union[int, None] = None, cluster_id: Union[int, None] = None
) -> Union[Cluster, None]:
    """Get cluster data from the backend API."""
    if node_id:
        cluster = await get(f"{url}/nodes/{node_id}/cluster", headers=headers)
    elif cluster_id:
        cluster = await get(f"{url}/clusters/{cluster_id}", headers=headers)
    else:
        logger.error("Either node_id or cluster_id must be provided")
        return None
    if cluster:
        return Cluster.model_validate(cluster)
    return None
