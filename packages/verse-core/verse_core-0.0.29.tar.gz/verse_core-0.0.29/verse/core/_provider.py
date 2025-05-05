import asyncio
from typing import Any

from ._arg_parser import ArgParser
from ._async_helper import AsyncHelper
from ._context import Context
from ._operation import Operation
from ._response import Response
from ._type_converter import TypeConverter
from .exceptions import NotSupportedError


class Provider:
    _component: Any

    def __init__(self, **kwargs):
        self._component = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setup__(self, context: Context | None = None) -> None:
        pass

    async def __asetup__(self, context: Context | None = None) -> None:
        await AsyncHelper.to_async(func=self.__setup__, context=context)

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        if operation is not None and operation.name is not None:
            func_name = operation.name
            func = getattr(self, func_name, None)
            if func is not None and callable(func):
                self.__setup__()
                args = TypeConverter.convert_args(func, operation.args or {})
                result = func(**args)
                return (
                    result
                    if isinstance(result, Response)
                    else Response(result=result)
                )

            afunc_name = f"a{operation.name}"
            afunc = getattr(self, afunc_name, None)
            if callable(afunc):
                asyncio.run(self.__asetup__())
                args = TypeConverter.convert_args(afunc, operation.args or {})
                result = asyncio.run(afunc(**args))
                return (
                    result
                    if isinstance(result, Response)
                    else Response(result=result)
                )

        raise NotSupportedError(
            operation.to_json() if operation is not None else None
        )

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        if operation is not None and operation.name is not None:
            afunc_name = f"a{operation.name}"
            afunc = getattr(self, afunc_name, None)
            if afunc is not None and callable(afunc):
                await self.__asetup__()
                args = TypeConverter.convert_args(afunc, operation.args or {})
                result = await afunc(**args)
                return (
                    result
                    if isinstance(result, Response)
                    else Response(result=result)
                )

        return await AsyncHelper.to_async(
            func=self.__run__,
            operation=operation,
            context=context,
            **kwargs,
        )

    def __supports__(self, feature: str) -> bool:
        return True

    def __execute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        operation = ArgParser.convert_execute_operation(statement, params)
        return self.__run__(operation, context)

    async def __aexecute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        operation = ArgParser.convert_execute_operation(statement, params)
        return await self.__arun__(operation, context)

    def get_component(self):
        return self._component
