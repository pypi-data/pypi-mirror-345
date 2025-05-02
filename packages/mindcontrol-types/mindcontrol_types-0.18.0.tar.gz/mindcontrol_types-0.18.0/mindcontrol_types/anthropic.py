from typing import Literal, Union, TypeAlias, Optional
from genotype import Model


AnthropicModelV1: TypeAlias = Union[Literal["claude-3-5-sonnet"], Literal["claude-3-opus"], Literal["claude-3-sonnet"], Literal["claude-3-haiku"]]
"""Anthropic model identifier."""


class AnthropicSettingsV1(Model):
    """Anthropic model settings."""

    type: Literal["anthropic"]
    """Settings type."""
    model: Optional[AnthropicModelV1] = None
    """Model identifier."""


AnthropicProviders: TypeAlias = Union[Literal["aws"], Literal["anthropic"], Literal["gcp"]]
"""Anthropic providers."""
