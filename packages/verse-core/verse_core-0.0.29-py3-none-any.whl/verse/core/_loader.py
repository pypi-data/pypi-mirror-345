from __future__ import annotations

import copy
import importlib
import importlib.util
import inspect
import os
import re
import sys
from enum import Enum
from typing import Any

from ._component import Component, Provider
from ._operation import Operation
from ._type_converter import TypeConverter
from .constants import ROOT_PACKAGE_NAME
from .dependency import ComponentNode, ProviderNode
from .exceptions import LoadError
from .manifest import (
    MANIFEST_FILE,
    Manifest,
    MiddlewareInstance,
    ProviderInstance,
)


class Loader:
    path: str
    manifest_path: str

    manifest: Manifest
    root: str

    _common_providers: list[str] = ["hosted"]
    _init = False
    _dependencies: dict[str, ComponentDependency] = dict()

    def __init__(
        self,
        path: str = ".",
        manifest: str = MANIFEST_FILE,
    ):
        self.path = path
        self.manifest_path = os.path.join(
            path,
            manifest,
        )
        self.manifest = Manifest.parse(path=self.manifest_path)
        if self.manifest.root is not None:
            self.root = self.manifest.root
        abs_project_folder = os.path.abspath(path)
        if abs_project_folder not in sys.path:
            sys.path.append(abs_project_folder)

    def generate_requirements(
        self,
        handle: str | None = None,
        tag: str | None = None,
        out: str | None = None,
    ) -> dict[str, list[str]]:
        requirements: dict[str, list[str]] = {"verse-core": []}

        def traverse(node: ComponentNode):
            cnamespace, cpackage = node.name.split(".", 1)
            if node.kind == "custom" or node.provider.kind == "custom":
                if node.provider.name == "hosted":
                    requirements["verse-core"].append("hosted")
            else:
                package = f"verse-{cnamespace}"
                extra = (
                    cpackage.replace("_", "-")
                    + "-"
                    + node.provider.name.replace("_", "-")
                )
                if package not in requirements:
                    requirements[package] = []
                if extra not in requirements[package]:
                    requirements[package].append(extra)

            for child in node.depends:
                traverse(child)
            for child in node.provider.depends:
                traverse(child)

        graph = self.get_dependency_graph(handle=handle, tag=tag)
        traverse(graph)

        if out is not None:
            content = ""
            for package in requirements:
                if len(requirements[package]) > 0:
                    content += (
                        package
                        + "["
                        + str.join(",", requirements[package])
                        + "]"
                        "\n"
                    )
                else:
                    content += package + "\n"
            with open(out, "w") as file:
                file.write(content)
        return requirements

    def get_component_name(self, handle: str | None = None) -> str:
        for component in self.manifest.components:
            if component.handle == handle:
                return component.name
        raise LoadError("Unresolved handle")

    def load_component(
        self,
        handle: str | None = None,
        tag: str | None = None,
    ) -> Component:
        component = self._resolve_component(
            handle=handle or self.root,
            tag=tag,
        ).component
        return component

    def get_dependency_graph(
        self,
        handle: str | None = None,
        tag: str | None = None,
    ) -> ComponentNode:
        def _get_node(component: ComponentDependency) -> ComponentNode:
            node = ComponentNode(
                handle=component.handle,
                name=component.name,
                kind=(
                    "custom"
                    if component.name.startswith("custom.")
                    else "base"
                ),
                provider=ProviderNode(
                    name=component.provider.name,
                    kind=(
                        "custom"
                        if component.provider.name.startswith("custom.")
                        else "base"
                    ),
                ),
            )
            dependencies = self._get_dependencies_from_param(
                value=component.parameters, tag=tag
            )
            for dependency in dependencies:
                node.depends.append(_get_node(dependency))

            dependencies = self._get_dependencies_from_param(
                value=component.provider.parameters, tag=tag
            )
            for dependency in dependencies:
                node.provider.depends.append(_get_node(dependency))
            return node

        self._prepare_unresolved(tag=tag)
        tagged_handle = self._get_tagged_handle(
            handle=self.root if handle is None else handle, tag=tag
        )
        return _get_node(self._dependencies[tagged_handle])

    def _resolve_component(
        self,
        handle: str,
        tag: str | None,
    ) -> ComponentDependency:
        tagged_handle = self._get_tagged_handle(handle=handle, tag=tag)
        if tagged_handle in self._dependencies:
            if self._dependencies[tagged_handle].resolved:
                return self._dependencies[tagged_handle]
            cdep = self._dependencies[tagged_handle]
        else:
            cdep = self._get_unresolved(handle=handle, tag=tag)
            self._dependencies[tagged_handle] = cdep
        cdep.parameters = self._resolve_param(
            cdep.parameters,
            tag,
        )
        pdep = cdep.provider
        pdep.parameters = self._resolve_param(
            pdep.parameters,
            tag,
        )
        pdep.provider = self._init_provider(pdep)
        pdep.resolved = True
        cdep.component = self._init_component(cdep, pdep.provider)
        cdep.component._handle = handle
        for mcdep in cdep.middleware:
            mcdep.parameters = self._resolve_param(
                mcdep.parameters,
                tag,
            )
            mpdep = mcdep.provider
            mpdep.parameters = self._resolve_param(
                mpdep.parameters,
                tag,
            )
            mpdep.provider = self._init_provider(mpdep)
            mpdep.resolved = True
            mcdep.component = self._init_component(mcdep, mpdep.provider)
            mcdep.component._handle = mcdep.handle
            mcdep.resolved = True
        if len(cdep.middleware) > 0:
            cdep.component.attach_middleware(
                middleware=[mcdep.component for mcdep in cdep.middleware]
            )
        cdep.resolved = True
        return cdep

    def _resolve_param(self, value: Any, tag: str | None) -> Any:
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._resolve_param(value=v, tag=tag)
            return value
        elif isinstance(value, list):
            for i, item in enumerate(value):
                value[i] = self._resolve_param(value=item, tag=tag)
            return value
        elif isinstance(value, str) and self._is_ref(value):
            ref_info = self._get_ref_info(value)
            if ref_info.type == RefType.COMPONENT:
                return self._resolve_component(
                    handle=ref_info.component_handle,
                    tag=ref_info.tag or tag,
                ).component
            elif ref_info.type == RefType.COMPONENT_GET:
                return self._resolve_component_get(
                    self._resolve_component(
                        handle=ref_info.component_handle,
                        tag=ref_info.tag or tag,
                    ).component,
                    ref_info.get_args,
                )
            elif ref_info.type == RefType.TAG:
                return tag
        return value

    def _get_dependencies_from_param(
        self,
        value: Any,
        tag: str | None,
    ) -> list[ComponentDependency]:
        dependencies: list = []
        if isinstance(value, dict):
            for k, v in value.items():
                dependencies.extend(
                    self._get_dependencies_from_param(value=v, tag=tag)
                )
        elif isinstance(value, list):
            for i, item in enumerate(value):
                dependencies.extend(
                    self._get_dependencies_from_param(value=item, tag=tag)
                )
        elif isinstance(value, str) and self._is_ref(value):
            ref_info = self._get_ref_info(value)
            tagged_handle = self._get_tagged_handle(
                handle=ref_info.component_handle, tag=tag
            )
            if tagged_handle in self._dependencies:
                dependencies.append(self._dependencies[tagged_handle])
            else:
                raise LoadError(f"Unresolved component {tagged_handle}")
        return dependencies

    def _init_component(
        self,
        cdep: ComponentDependency,
        provider: Provider,
    ) -> Component:
        path = cdep.py_path
        if cdep.py_path is not None and cdep.py_path.startswith("."):
            path = os.path.join(
                self.path,
                cdep.name,
                cdep.py_path,
            )
        component = Loader.load_component_instance(
            path=path,
            parameters=cdep.parameters,
            provider=provider,
        )
        return component

    def _init_provider(self, pdep: ProviderDependency) -> Provider:
        path = pdep.py_path
        if pdep.py_path is not None and pdep.py_path.startswith("."):
            path = os.path.join(
                self.path,
                pdep.component_name,
                pdep.py_path,
            )
        provider = Loader.load_provider_instance(
            path=path,
            parameters=pdep.parameters,
        )
        return provider

    def _get_unresolved(
        self,
        handle: str,
        tag: str | None = None,
    ) -> ComponentDependency:
        for component in self.manifest.components:
            if component.handle == handle:
                return self._prepare_component_dependency(
                    component.handle,
                    component.name,
                    component.parameters,
                    component.provider,
                    component.middleware,
                    tag,
                )
        raise LoadError(f"Unresolved component {handle}")

    def _prepare_unresolved(
        self,
        tag: str | None = None,
    ):
        for component in self.manifest.components:
            tagged_handle = self._get_tagged_handle(
                handle=component.handle, tag=tag
            )
            if tagged_handle in self._dependencies:
                continue
            cdep = self._prepare_component_dependency(
                component.handle,
                component.name,
                component.parameters,
                component.provider,
                component.middleware,
                tag,
            )
            self._dependencies[tagged_handle] = cdep

    def _prepare_component_dependency(
        self,
        handle: str,
        name: str,
        parameters: dict[str, Any],
        provider: ProviderInstance | list[ProviderInstance],
        middleware: list[MiddlewareInstance],
        tag: str | None = None,
    ):
        cdep = ComponentDependency()
        cdep.handle = handle
        cdep.name = name
        cdep.parameters = copy.deepcopy(parameters)
        cnamespace, cpackage = name.split(".", 1)
        if cnamespace == "custom":
            cdep.py_path = f"{cpackage}.component"
        else:
            cdep.py_path = (
                f"{ROOT_PACKAGE_NAME}.{cnamespace}.{cpackage}.component"
            )
        if isinstance(provider, ProviderInstance):
            pi = provider
        elif isinstance(provider, list):
            found = False
            for p in provider:
                if self._check_tag(tag=p.tag, check_tag=tag):
                    pi = p
                    found = True
                    break
            if not found:
                pi = provider[0]
        pdep = ProviderDependency()
        pdep.component_name = name
        pdep.name = pi.name
        pdep.parameters = copy.deepcopy(pi.parameters)
        if cnamespace == "custom" or pi.name.startswith("custom."):
            ppackage = pi.name.split(".")[-1]
            if ppackage in self._common_providers:
                pdep.py_path = (
                    f"{ROOT_PACKAGE_NAME}.internal.providers.{ppackage}"
                )
            else:
                pdep.py_path = f"{cpackage}.providers.{ppackage}"
        else:
            cnamespace = f"{ROOT_PACKAGE_NAME}.{cnamespace}.{cpackage}"
            pdep.py_path = f"{cnamespace}.providers.{pi.name}"
        pdep.resolved = False
        cdep.provider = pdep
        cdep.resolved = False
        for mc in middleware:
            if self._check_tag(mc.tag, tag):
                mcdep = self._prepare_component_dependency(
                    handle=mc.handle or mc.name,
                    name=mc.name,
                    parameters=mc.parameters,
                    provider=mc.provider,
                    middleware=[],
                    tag=tag,
                )
                cdep.middleware.append(mcdep)
        return cdep

    def _check_tag(
        self, tag: str | list[str] | None, check_tag: str | None
    ) -> bool:
        if tag is None:
            return True
        if isinstance(tag, str):
            return tag == check_tag
        if isinstance(tag, list):
            return check_tag in tag
        return False

    def _resolve_component_get(self, component: Component, get_args: dict):
        res = component.__run__(operation=Operation(name="get", args=get_args))
        return res.result.value

    def _resolve_provider_get(self, provider: Provider, get_args: dict):
        res = provider.__run__(operation=Operation(name="get", args=get_args))
        return res.result.value

    def _get_ref_info(self, str: str):
        pattern = r"^\{\{(.+)\}\}$"
        match = re.match(pattern, str)
        if not match:
            raise LoadError(f"{str} not a ref")
        value = match.group(1)
        ref_info = RefInfo()
        if value == "__tag__":
            ref_info.type = RefType.TAG
            return ref_info
        splits = value.split(".")
        component_splits = splits[0].split(":")
        ref_info.component_handle = component_splits[0]
        ref_info.tag = (
            component_splits[1] if len(component_splits) == 2 else None
        )
        if len(splits) == 1:
            ref_info.type = RefType.COMPONENT
        elif len(splits) == 2:
            ref_info.type = RefType.COMPONENT_GET
            ref_info.get_args = dict(key=dict(id=splits[1]))
        elif len(splits) == 3:
            ref_info.type = RefType.COMPONENT_GET
            ref_info.get_args = dict(key=dict(label=splits[1], id=splits[2]))
        return ref_info

    def _is_ref(self, str: str) -> bool:
        pattern = r"^\{\{.+\}\}$"
        return bool(re.match(pattern, str))

    def _get_path(self, base_dir: str, manifest_path: str):
        return os.path.join(base_dir, manifest_path)

    def _get_tagged_middleware_handle(
        self,
        component_handle: str,
        middleware_handle: str,
        tag: str | None = None,
    ):
        tagged_handle = self._get_tagged_handle(
            handle=component_handle, tag=tag
        )
        return f"{tagged_handle}${middleware_handle}"

    def _get_tagged_handle(self, handle: str, tag: str | None = None):
        if not tag:
            return handle
        return f"{handle}:{tag}"

    @staticmethod
    def load_provider_instance(
        path: str | None = None,
        parameters: dict[str, Any] = dict(),
    ) -> Provider:
        if path is None:
            return Provider(**parameters)
        provider = Loader.load_class(path, Provider)
        converted_parameters = TypeConverter.convert_args(
            provider.__init__, parameters
        )
        return provider(**converted_parameters)

    @staticmethod
    def load_component_instance(
        path: str | None,
        parameters: dict,
        provider: Provider,
    ) -> Component:
        if path is None:
            return Component(provider=provider, **parameters)
        component = Loader.load_class(path, Component)
        converted_parameters = TypeConverter.convert_args(
            component.__init__, parameters
        )
        return component(provider=provider, **converted_parameters)

    @staticmethod
    def load_class(path: str, type: Any) -> Any:
        class_name = None
        if ":" in path:
            splits = path.split(":")
            module_name = splits[0]
            class_name = splits[-1]
        else:
            module_name = path
        if module_name.endswith(".py"):
            import sys

            normalized_module_name = (
                os.path.normpath(module_name)
                .replace("\\", "/")
                .split(".py")[0]
                .replace("/", ".")
                .lstrip(".")
            )
            spec = importlib.util.spec_from_file_location(
                normalized_module_name, os.path.abspath(path)
            )
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                sys.modules[normalized_module_name] = module
                if spec.loader is not None:
                    spec.loader.exec_module(module)
            module_name = normalized_module_name
        else:
            module = importlib.import_module(module_name)
        if class_name is not None:
            return getattr(module, class_name)
        else:
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, type) and cls.__module__ == module_name:
                    return cls
        raise LoadError(f"{type.__name__} not found at {module}")


class RefInfo:
    type: RefType
    component_handle: str
    get_args: dict
    tag: str | None

    def __init__(self):
        self.tag = None


class RefType(int, Enum):
    COMPONENT = 0
    COMPONENT_GET = 1
    TAG = 2


class ComponentDependency:
    handle: str
    name: str
    parameters: dict[str, Any]
    py_path: str | None
    provider: ProviderDependency
    component: Component
    middleware: list[ComponentDependency]
    tag: str | None
    resolved: bool = False

    def __init__(self):
        self.middleware = []
        self.parameters = dict()


class ProviderDependency:
    component_name: str
    name: str
    parameters: dict[str, Any]
    py_path: str | None
    provider: Provider
    resolved: bool = False

    def __init__(self):
        self.parameters = dict()
