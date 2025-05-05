from __future__ import annotations

from .data_model import DataModel


class ComponentNode(DataModel):
    handle: str
    name: str
    kind: str
    provider: ProviderNode
    depends: list[ComponentNode] = []


class ProviderNode(DataModel):
    name: str
    kind: str
    depends: list[ComponentNode] = []
