from .anthropic import AnthropicSettingsV1
from .openai import OpenAISettingsV1
from typing import Union, TypeAlias, Optional
from typing_extensions import Annotated
from pydantic import Field
from genotype import Model


class SettingsNope(Model):
    """Fallback for when no settings are provided. It is needed to fallback for
    older payloads with empty settings object."""

    type: Optional[None] = None
    model: Optional[None] = None


SettingsV1: TypeAlias = Annotated[Union[SettingsNope, AnthropicSettingsV1, OpenAISettingsV1], Field(json_schema_extra={'discriminator': 'type'})]
