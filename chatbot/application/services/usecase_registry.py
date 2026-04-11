from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from chatbot.application.protocols.usecase import UseCase


class UseCaseRegistry[Input_co: BaseModel]:
    def __init__(self) -> None:
        self._registry_by_name: dict[str, UseCase[Input_co, Any]] = {}

    def register_step(self, handler: UseCase[Input_co, Any]) -> None:
        self._registry_by_name[handler.name.lower()] = handler

    def _get_handler_by_name(self, name: str | None) -> UseCase[Input_co, Any] | None:
        return self._registry_by_name.get((name or "").lower())

    async def run(self, payload: dict[str, str], *, name: str) -> BaseModel | None:
        if name and (handler := self._get_handler_by_name(name)):
            result: BaseModel = await handler.execute(
                handler.input_schema.model_validate(payload)
            )
            return result
        return None
