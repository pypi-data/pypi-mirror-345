from abc import ABC, abstractmethod
from typing import Optional, List

from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.entities.processing_case_filters import ProcessingCaseFilters


class ProcessingCaseRepository(ABC):

    @abstractmethod
    def find(self, uuid: str, include_items: bool = False) -> Optional[ProcessingCase]:
        raise NotImplementedError

    @abstractmethod
    def persist(self, instance: ProcessingCase) -> ProcessingCase:
        raise NotImplementedError

    @abstractmethod
    def remove(self, instance: ProcessingCase):
        raise NotImplementedError

    @abstractmethod
    def filter(self, filters: ProcessingCaseFilters) -> List[ProcessingCase]:
        raise NotImplementedError
