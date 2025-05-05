from __future__ import annotations

from .data_model import DataModel


class BaseContext(DataModel):
    component: str | None = None
    provider: str | None = None
    handle: str | None = None
    info: dict | None = None
    start_time: float | None = None
    latency: float | None = None
    children: list[BaseContext] = []


class Context(BaseContext):
    run_id: str
    parent: Context | None = None
