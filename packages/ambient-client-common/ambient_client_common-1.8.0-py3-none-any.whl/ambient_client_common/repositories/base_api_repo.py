from typing import Union

import aiohttp

from ambient_client_common.utils import logger


async def get(url: str, headers: dict) -> Union[list, dict, None]:
    """Get data from the local API."""
    logger.debug("Calling GET - {} ...", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                response.raise_for_status()
                logger.debug(
                    "received succcessful response. status: {}, url: {}",
                    response.status,
                    url,
                )
                return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    logger.warning(
                        "Error: {}. Status: {}, URL: {}", e, response.status, url
                    )
                    return None
                logger.error("Error: {}. Status: {}, URL: {}", e, response.status, url)
                raise e


async def put(url: str, headers: dict, data: dict) -> Union[list, dict, None]:
    """Put data to the local API."""
    logger.debug("Calling PUT - {} ...", url)
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=data) as response:
            try:
                response.raise_for_status()
                logger.debug(
                    "received succcessful response. status: {}, url: {}",
                    response.status,
                    url,
                )
                return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    logger.warning(
                        "Error: {}. Status: {}, URL: {}", e, response.status, url
                    )
                    return None
                logger.error("Error: {}. Status: {}, URL: {}", e, response.status, url)
                raise e


async def post(
    url: str, headers: dict, data: Union[dict, None] = None
) -> Union[list, dict, None]:
    """Post data to the local API."""
    logger.debug("Calling POST - {} ...", url)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            try:
                response.raise_for_status()
                logger.debug(
                    "received succcessful response. status: {}, url: {}",
                    response.status,
                    url,
                )
                return await response.json()
            except aiohttp.ClientResponseError as e:
                logger.error("Error: {}. Status: {}, URL: {}", e, response.status, url)
                raise e


async def delete(url: str, headers: dict) -> Union[list, dict, None]:
    """Delete data from the local API."""
    logger.debug("Calling DELETE - {} ...", url)
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            try:
                response.raise_for_status()
                logger.debug(
                    "received succcessful response. status: {}, url: {}",
                    response.status,
                    url,
                )
                return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    logger.warning(
                        "Error: {}. Status: {}, URL: {}", e, response.status, url
                    )
                    return None
                logger.error("Error: {}. Status: {}, URL: {}", e, response.status, url)
                raise e


async def patch(url: str, headers: dict, data: dict) -> Union[list, dict, None]:
    """Patch data to the local API."""
    logger.debug("Calling PATCH - {} ...", url)
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=data) as response:
            try:
                response.raise_for_status()
                logger.debug(
                    "received succcessful response. status: {}, url: {}",
                    response.status,
                    url,
                )
                return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    logger.warning(
                        "Error: {}. Status: {}, URL: {}", e, response.status, url
                    )
                    return None
                logger.error("Error: {}. Status: {}, URL: {}", e, response.status, url)
                raise e
