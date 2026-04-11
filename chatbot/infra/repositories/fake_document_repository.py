from uuid import UUID

from chatbot.domain.entities.application_document import ApplicationDocument


class FakeDocumentRepository:
    def __init__(
        self,
        seed: list[ApplicationDocument] = [],
        direct_return: ApplicationDocument | None = None,
    ) -> None:
        self.direct_return = direct_return
        self.by_application_id: dict[UUID, ApplicationDocument] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[ApplicationDocument]) -> None:
        for item in seed:
            self.by_application_id[item.application_id] = item

    async def get_by_application_id(
        self, application_id: UUID
    ) -> ApplicationDocument | None:
        if self.direct_return:
            return self.direct_return
        return self.by_application_id.get(application_id)
