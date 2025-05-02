from typing import Union, TypeAlias, Literal, Dict, Optional
from typing_extensions import Annotated
from pydantic import Field
from genotype import Model
from .openai import OpenAIProviders
from .anthropic import AnthropicProviders


PackageNpmDependencies: TypeAlias = Dict[str, str]
"""npm package dependencies."""


class PackageNpm(Model):
    """npm package."""

    type: Literal["npm"]
    """Package type."""
    name: str
    """Package name."""
    version: str
    """Package version."""
    shasum: str
    """SHA1 checksum."""
    tarball: str
    """Tarball URL."""
    tag: str
    """Tag name."""
    time: int
    """Unix timestamp in milliseconds."""
    dependencies: PackageNpmDependencies
    """Package dependencies."""


class PackagePip(Model):
    """Pip package."""

    type: Literal["pip"]
    """Package type."""
    name: str
    """Package name."""
    version: str
    """Package version."""
    sha256: str
    """SHA-256 checksum."""
    wheel: str
    """Wheel file URL."""


Package: TypeAlias = Annotated[Union[PackageNpm, PackagePip], Field(json_schema_extra={'discriminator': 'type'})]
"""Collection package."""


class PackageSettingsProviders(Model):
    """Providers map"""

    openai: Optional[OpenAIProviders] = None
    """OpenAI provider."""
    anthropic: Optional[AnthropicProviders] = None
    """Anthropic provider."""


class PackageSettings(Model):
    """Package settings."""

    providers: Optional[PackageSettingsProviders] = None
    """Package providers."""


PackageStatus: TypeAlias = Union[Literal["pending"], Literal["building"], Literal["errored"], Literal["published"]]
"""Status of the package."""


class PackageTrigger(Model):
    """Package trigger message."""

    id: int
    """Package id."""
