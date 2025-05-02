import base64
import functools
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Union

import aiohttp
import apluggy as pluggy
from ambient_base_plugin.models.configuration import ConfigPayload
from ambient_base_plugin.models.message import Message

from ambient_client_common import config
from ambient_client_common.utils import logger

hookspec = pluggy.HookspecMarker("ambient_system_sweep")
hookimpl = pluggy.HookimplMarker("ambient_system_sweep")


def edge_server_token_manager(func):
    @functools.wraps(func)
    async def wrap(self, *args, **kwargs):
        logger.debug("In edge_server_token_manager")
        if not self.config_payload.password:
            logger.error("Password is not set")
            raise ValueError("Password is not set")

        logger.contextualize(plugin_name=self.config_payload.plugin_config.name)
        decoded_token = (
            f"{self.config_payload.plugin_config.name}:{self.config_payload.password}"
        )
        logger.debug(f"Decoded token: {decoded_token}")
        encoded_token = base64.b64encode(decoded_token.encode()).decode()
        local_headers = {
            "Authorization": f"Basic {encoded_token}",
        }
        if "local_headers" in kwargs:
            kwargs["local_headers"].update(local_headers)
        else:
            kwargs["local_headers"] = local_headers
        logger.debug(f"Local headers: {kwargs['local_headers']}")
        return await func(self, *args, **kwargs)

    return wrap


@edge_server_token_manager
async def get_api_token(self, *args, **kwargs) -> Union[str, None]:
    """Get token for the plugin."""
    logger.debug("In get_api_token")
    url = f"{config.settings.edge_server_url}/auth/token"
    headers = kwargs.get("local_headers", {})
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                response.raise_for_status()
                response_data: dict = await response.json()
                token = response_data.get("token", None)
                logger.debug("got token from client server: %s", token)
                return token
            except aiohttp.ClientResponseError as e:
                logger.error(f"Error getting token: {e}")
                raise e


@edge_server_token_manager
async def refresh_api_token(self, *args, **kwargs) -> aiohttp.ClientResponse:
    """Refresh token for the plugin."""
    url = f"{config.settings.edge_server_url}/auth/refresh"
    headers = kwargs.get("local_headers", {})
    async with aiohttp.ClientSession() as session:
        async with session.request(
            self.config_payload.api_url, url, headers=headers
        ) as response:
            return response


def api_token_manager(func):
    @functools.wraps(func)
    async def wrap(self, *args, **kwargs):
        token = await get_api_token(self)
        if not token:
            raise ValueError("Token is not set")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers
        try:
            return await func(self, *args, **kwargs)
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                await refresh_api_token(self)
                token = await get_api_token(self)
                kwargs["headers"]["Authorization"] = f"Bearer {token}"
                return await func(self, *args, **kwargs)
            raise e

    return wrap


class BasePlugin(ABC):
    @abstractmethod
    async def configure(
        self, config: ConfigPayload, logger: Union[Logger, Any] = None
    ) -> None:
        pass

    @abstractmethod
    async def handle_event(self, message: Message, *args, **kwargs) -> None:
        pass

    # Why isn't this an abstract method? Because it is not
    # required for all plugins to implement this method.
    # Reversion count: 1
    @hookspec
    async def run_system_sweep(self) -> None:
        pass
