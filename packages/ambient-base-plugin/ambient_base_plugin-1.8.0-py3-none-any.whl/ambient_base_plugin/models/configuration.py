from typing import List, Optional

from pydantic import BaseModel, field_validator

from ambient_client_common.utils.consistent_hash import consistent_hash


class RetryPolicy(BaseModel):
    max_retries: int = 0
    retry_interval: int = 1  # Time interval between retries in seconds
    backoff_factor: int = 2  # Exponential backoff factor (1, 2, 4, 8)


class PluginDefinition(BaseModel):
    name: str
    topics: List[str]
    module: str
    class_name: str
    extra_data: Optional[dict] = None
    retry_policy: Optional[RetryPolicy] = None

    # ensure topics start with / or * and ends without /
    @field_validator("topics")
    def validate_topics(cls, values: List[str]):
        for value in values:
            if not value.startswith("/") and not value.startswith("*"):
                raise ValueError(f"Topic must start with / or *. Topic: {value}")
            if value.endswith("/"):
                raise ValueError(f"Topic must not end with /. Topic: {value}")
        return values


class ConfigPayload(BaseModel):
    node_id: int
    plugin_config: PluginDefinition
    api_url: str
    extra_data: Optional[dict] = None

    # data available on request
    platform: Optional[str] = None
    password: Optional[str] = None

    @property
    def password_hash(self) -> str:
        """
        Generate a consistent hash for the password.
        """
        if self.password:
            return consistent_hash(self.password)
        return ""
