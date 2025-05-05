from __future__ import annotations

from typing import Any

from ._yaml_loader import YamlLoader
from .data_model import DataModel

__all__ = [
    "ComponentInstance",
    "Manifest",
    "MiddlewareInstance",
    "ProviderInstance",
    "MANIFEST_FILE",
]


MANIFEST_FILE = "manifest.yaml"


class ProviderInstance(DataModel):
    name: str
    parameters: dict[str, Any] = dict()
    tag: str | list[str] | None = None


class ComponentInstance(DataModel):
    handle: str
    name: str
    parameters: dict[str, Any] = dict()
    provider: ProviderInstance | list[ProviderInstance] = ProviderInstance(
        name="default"
    )
    middleware: list[MiddlewareInstance] = []


class MiddlewareInstance(DataModel):
    handle: str | None = None
    name: str
    parameters: dict[str, Any] = dict()
    provider: ProviderInstance | list[ProviderInstance] = ProviderInstance(
        name="default"
    )
    tag: str | list[str] | None = None


class Manifest(DataModel):
    components: list[ComponentInstance] = []
    root: str | None = None

    @staticmethod
    def parse(path: str) -> Manifest:
        obj = YamlLoader.load(path=path)
        manifest = Manifest.from_dict(obj)
        return manifest
