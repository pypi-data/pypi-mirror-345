from typing import List, Optional, Literal, Union, TypeAlias
from .settings import SettingsV1
from genotype import Model


PromptMessageV1Role: TypeAlias = Union[Literal["user"], Literal["assistant"]]


class PromptMessageV1(Model):
    """Prompt message."""

    role: PromptMessageV1Role
    """Message role."""
    content: str
    """Message content."""


class PromptV1(Model):
    """Prompt object."""

    messages: List[PromptMessageV1]
    """Prompt messages."""
    system: Optional[str] = None
    """System model instructions."""
    settings: Optional[SettingsV1] = None
    """Model settings."""
