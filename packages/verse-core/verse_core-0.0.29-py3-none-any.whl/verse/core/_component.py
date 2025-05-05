from __future__ import annotations

import time
import uuid
from typing import Any

from ._context import BaseContext, Context
from ._operation import Operation
from ._provider import Provider
from ._response import Response


class Component:
    _provider: Provider
    _middleware: list[Component]
    _debug: bool
    _unpack: bool
    _handle: str | None

    def __init__(
        self,
        **kwargs,
    ):
        self._debug = kwargs.pop("_debug", False)
        self._unpack = kwargs.pop("_unpack", False)
        self._handle = None
        self.attach_middleware(middleware=kwargs.pop("middleware", []))
        self.attach_provider(provider=kwargs.pop("provider", "default"))

    def attach_provider(
        self,
        provider: Provider | dict | str,
    ) -> None:
        if isinstance(provider, Provider):
            provider._component = self
            self._provider = provider
        else:
            if isinstance(provider, dict):
                name = provider.pop("name")
                parameters = provider.pop("parameters", dict())
            elif isinstance(provider, str):
                name = provider
                parameters = dict()
            from ._loader import Loader

            module_name = self.__class__.__module__.rsplit(".", 1)[0]
            provider_path = f"{module_name}.providers.{name}"
            provider_instance = Loader.load_provider_instance(
                path=provider_path,
                parameters=parameters,
            )
            self.attach_provider(provider=provider_instance)

    def attach_middleware(self, middleware: list[Component]) -> None:
        self._middleware = middleware
        for i in range(len(middleware)):
            if i + 1 < len(middleware):
                setattr(middleware[i], "component", middleware[i + 1])
            else:
                setattr(middleware[i], "component", self)

    def __setup__(self, context: Context | None = None) -> None:
        self._provider.__setup__(context=context)

    async def __asetup__(self, context: Context | None = None) -> None:
        await self._provider.__asetup__(context=context)

    def __run__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        if len(self._middleware) > 0:
            return self._middleware[0].__run__(
                operation=operation, context=context, **kwargs
            )
        else:
            return self.__run_without_middleware__(
                operation=operation, context=context, **kwargs
            )

    async def __arun__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        if len(self._middleware) > 0:
            return await self._middleware[0].__run__(
                operation=operation, context=context, **kwargs
            )
        else:
            return await self.__arun_without_middleware__(
                operation=operation, context=context, **kwargs
            )

    def __run_without_middleware__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        parent_context = self._convert_context(context)
        current_context = self._init_context(
            parent_context, kwargs.pop("context_info", None)
        )
        response = self._provider.__run__(
            operation=self._convert_operation(operation),
            context=current_context,
            **kwargs,
        )
        if isinstance(response, Response):
            if response.context is not None:
                current_context = response.context
        else:
            response = Response(result=response)
        self._finalize_context(parent_context, current_context)
        response.context = parent_context
        if not self._debug:
            response.native = None
        if self._unpack:
            return response.result
        return response

    async def __arun_without_middleware__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        parent_context = self._convert_context(context)
        current_context = self._init_context(
            parent_context, kwargs.pop("context_info", None)
        )
        response = await self._provider.__arun__(
            operation=self._convert_operation(operation),
            context=current_context,
            **kwargs,
        )
        if isinstance(response, Response):
            if response.context is not None:
                current_context = response.context
        else:
            response = Response(result=response)
        self._finalize_context(parent_context, current_context)
        response.context = parent_context
        if not self._debug:
            response.native = None
        if self._unpack:
            return response.result
        return response

    def __supports__(self, feature: str) -> bool:
        return self._provider.__supports__(feature)

    def __execute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._provider.__execute__(statement, params, context, **kwargs)

    async def __aexecute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self._provider.__aexecute__(
            statement, params, context, **kwargs
        )

    def _convert_operation(
        self,
        operation: dict | str | Operation | None,
    ) -> Operation | None:
        if isinstance(operation, dict):
            return Operation.from_dict(operation)
        elif isinstance(operation, str):
            return Operation(name=operation)
        return operation

    def _convert_context(
        self,
        context: dict | Context | None,
    ) -> Context | None:
        if isinstance(context, dict):
            return Context.from_dict(context)
        if context is None:
            return None
        return context

    def _init_context(
        self,
        parent_context: Context | None,
        context_info: dict | None,
    ) -> Context:
        provider_name = self._provider.__module__.split(".")[-1]
        component_name = self.__module__.split(".")[-2]
        if parent_context is not None:
            run_id = parent_context.run_id
        else:
            run_id = str(uuid.uuid4())
        ctx = Context(
            run_id=run_id,
            component=component_name,
            provider=provider_name,
            handle=self._handle,
            start_time=time.time(),
            parent=parent_context,
        )
        if parent_context is not None and parent_context.info is not None:
            ctx.info = parent_context.info
        if context_info is not None and ctx.info is None:
            ctx.info = context_info
        elif context_info is not None and ctx.info is not None:
            ctx.info = ctx.info | context_info
        return ctx

    def _finalize_context(
        self,
        parent_context: Context | None,
        current_context: Context,
    ):
        end_time = time.time()
        if current_context.start_time:
            current_context.latency = end_time - current_context.start_time
        if parent_context is not None:
            parent_context.children.append(
                BaseContext(
                    component=current_context.component,
                    provider=current_context.provider,
                    handle=current_context.handle,
                    info=current_context.info,
                    start_time=current_context.start_time,
                    latency=current_context.latency,
                    children=current_context.children,
                )
            )

    def _get_name(self):
        module_name = self.__class__.__module__.rsplit(".", 1)[0]
        if "." in module_name:
            return ".".join(module_name.split(".")[-2:])
        return f"custom.{module_name}"
