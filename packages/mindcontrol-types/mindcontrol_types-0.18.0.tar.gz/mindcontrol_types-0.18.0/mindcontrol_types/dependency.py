from typing import TypeAlias, Literal, Union
from genotype import Model


class DependencyProviderV1(Model):
    """Provider dependency."""

    type: Literal["provider"]
    """Dependency type."""
    id: Union[Literal["openai"], Literal["azure"], Literal["aws"], Literal["anthropic"], Literal["gcp"]]
    """Provider id."""


DependencyV1: TypeAlias = DependencyProviderV1
