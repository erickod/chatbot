from __future__ import annotations

from typing import Protocol, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class UseCase(Protocol[Input, Output]):
    input_schema: type[Input]
    output_schema: type[Output]
    name: str

    async def execute(self, input: Input) -> Output: ...
