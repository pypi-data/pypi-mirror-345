from abc import ABC, abstractmethod
from typing import Optional, List

from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters


class ProcessingCaseItemRepository(ABC):

    @abstractmethod
    def find(self, uuid: str) -> Optional[ProcessingCaseItem]:
        raise NotImplementedError

    @abstractmethod
    def find_by_digest(self, digest: str) -> Optional[ProcessingCaseItem]:
        raise NotImplementedError

    @abstractmethod
    def persist(self, instance: ProcessingCaseItem) -> ProcessingCaseItem:
        raise NotImplementedError

    @abstractmethod
    def remove(self, instance: ProcessingCaseItem):
        raise NotImplementedError

    @abstractmethod
    def filter(
        self,
        filters: ProcessingCaseItemFilters,
    ) -> List[ProcessingCaseItem]:
        raise NotImplementedError
