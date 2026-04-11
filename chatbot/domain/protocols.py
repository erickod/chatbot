from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Generic, Self, TypeVar, cast
from uuid import UUID, uuid7

from pydantic import BaseModel

S = TypeVar("S")


class StepFSM(Generic[S]):
    """Classe base genérica para FSMs de step.

    Subclasses devem declarar os atributos de classe:
        _transitions: dict[S, list[S]]
        _reversible_transitions: dict[S, list[S]]
        _final_states: frozenset[S]
        _failed_states: frozenset[S]
    """

    _transitions: dict[S, list[S]]  # type: ignore[misc]
    _reversible_transitions: dict[S, list[S]]
    _final_states: frozenset[S]  # type: ignore[misc]
    _failed_states: frozenset[S]  # type: ignore[misc]

    def __init__(self, value: S) -> None:
        self.value = value

    def is_final(self) -> bool:
        return self.value in self._final_states

    def is_failed(self) -> bool:
        return self.value in self._failed_states

    def transitional_statuses(self) -> frozenset[S]:
        return frozenset(self._transitions.keys())

    def final_statuses(self) -> list[S]:
        return list(self._final_states)

    def get_next_statuses(self) -> list[Self]:
        return [type(self)(s) for s in self._transitions.get(self.value, [])]

    def get_incoming_statuses(self) -> list[Self]:
        reverse = self._build_reverse()
        return [type(self)(s) for s in reverse.get(self.value, [])]

    def _build_reverse(self) -> dict[S, list[S]]:
        result: dict[S, list[S]] = defaultdict(list)  # type: ignore[type-arg]
        for current, nexts in self._transitions.items():
            for nxt in nexts:
                result[nxt].append(current)
        return result

    def advance(self, status: S) -> bool:
        """Advance to the given status if the transition is valid."""
        allowed = self._transitions.get(self.value)
        if allowed is not None and status in allowed:
            self.value = cast(S, status)
            return True
        return False

    def reverse(self, status: S) -> bool:
        """Go back to the given status if the transition is valid."""
        allowed = self._reversible_transitions.get(self.value)
        if allowed is not None and status in allowed:
            self.value = cast(S, status)
            return True
        return False


class NameStepInput(BaseModel):
    originator_phone: str
    company_phone: str
    value: str


class NameStepOutput(BaseModel):
    status: str
    value: str
    step_name: str


class SaveNameStep:
    input_schema: type[NameStepInput] = NameStepInput
    output_schema: type[NameStepOutput] = NameStepOutput
    name: str = "name"

    def execute(self, input: NameStepInput) -> NameStepOutput:
        status = "COMPLETED"
        return NameStepOutput(status=status, value=input.value, step_name=self.name)


class Application[Input_co: BaseModel]:
    id: UUID
    status: str

    def register_handler(self, input: StepExecution): ...


class StepExecution(BaseModel):
    id: UUID
    application_id: UUID
    step_name: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    data: dict[str, Any] = {}
    fsm: StepFSM


class NameStepFSM(StepFSM): ...


class NameStepExecution(StepExecution):
    fsm: StepFSM = NameStepFSM("STARTED")

    @classmethod
    def create(cls, name: str) -> "NameStepExecution":
        return cls(
            id=uuid7(),
            application_id=uuid7(),
            step_name="NAME",
            created_at=datetime.now(tz=timezone.utc),
            data={"value": name},
        )

    @property
    def status(self) -> str:
        if not self.data.get("value"):
            return "PENDING"
        return "COMPLETED"


class NationalIDStepExecution(StepExecution):
    fsm: StepFSM = NameStepFSM("STARTED")

    @classmethod
    def create(cls, national_id: str) -> "NationalIDStepExecution":
        return cls(
            id=uuid7(),
            application_id=uuid7(),
            step_name="NAME",
            created_at=datetime.now(tz=timezone.utc),
            data={"value": national_id},
        )

    @property
    def status(self) -> str:
        if not self.data.get("value"):
            return "PENDING"
        return "COMPLETED"


class ContactStepExecution(StepExecution):
    fsm: StepFSM = NameStepFSM("STARTED")

    @classmethod
    def create(
        cls, national_id: str, email: str, name: str, role: str
    ) -> "ContactStepExecution":
        return cls(
            id=uuid7(),
            application_id=uuid7(),
            step_name="ContactStepExecution",
            created_at=datetime.now(tz=timezone.utc),
            data={
                "national_id": national_id,
                "email": email,
                "name": name,
                "role": role,
            },
        )

    @property
    def status(self) -> str:
        if not self.data.get("value"):
            return "PENDING"
        return "COMPLETED"


class SellerContactStepExecution(StepExecution):
    fsm: StepFSM = NameStepFSM("STARTED")

    @classmethod
    def create(
        cls, name: str, whatsapp: str, role: str
    ) -> "SellerContactStepExecution":
        return cls(
            id=uuid7(),
            application_id=uuid7(),
            step_name="ContactStepExecution",
            created_at=datetime.now(tz=timezone.utc),
            data={"name": name, "whatsapp": whatsapp, "role": role},
        )

    @property
    def status(self) -> str:
        if not self.data.get("value"):
            return "PENDING"
        return "COMPLETED"


class BiometricSessionStepExecution(StepExecution):
    fsm: StepFSM = NameStepFSM("STARTED")

    @classmethod
    def create(
        cls, name: str, whatsapp: str, role: str
    ) -> "SellerContactStepExecution":
        return cls(
            id=uuid7(),
            application_id=uuid7(),
            step_name="BiometricSessionStepExecution",
            created_at=datetime.now(tz=timezone.utc),
            data={"name": name, "whatsapp": whatsapp, "role": role},
        )

    @property
    def status(self) -> str:
        if not self.data.get("value"):
            return "PENDING"
        return "COMPLETED"


application = Application()
# application.transit("name", "John Doe")
