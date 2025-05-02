from .dependency import DependencyV1
from .resource import ResourceV1
from typing import Literal, List
from genotype import Model


class PayloadV1(Model):
    v: Literal[1]
    """Schema version"""
    dependencies: List[DependencyV1]
    """Dependencies."""
    resources: List[ResourceV1]
    """Resources."""
