from dataclasses import dataclass
from typing import List, Optional

from requests import Response

from documente_shared.application.payloads import camel_to_snake
from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters
from documente_shared.domain.repositories.processing_case_item import ProcessingCaseItemRepository
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpProcessingCaseItemRepository(
    DocumenteClientMixin,
    ProcessingCaseItemRepository,
):
    def find(self, uuid: str) -> Optional[ProcessingCaseItem]:
        response = self.session.get(f"{self.api_url}/v1/processing-case-items/{uuid}/")
        if response.status_code == 200:
            return self._build_processing_case_item(response)
        return None

    def find_by_digest(self, digest: str) -> Optional[ProcessingCaseItem]:
        response = self.session.get(f"{self.api_url}/v1/processing-case-items/{digest}/")
        if response.status_code == 200:
            return self._build_processing_case_item(response)
        return None

    def persist(self, instance: ProcessingCaseItem) -> ProcessingCaseItem:
        response: Response = self.session.put(
            url=f"{self.api_url}/v1/processing-case-items/{instance.uuid}/",
            json=instance.to_persist_dict,
        )
        if response.status_code in [200, 201]:
            return self._build_processing_case_item(response)
        return instance

    def remove(self, instance: ProcessingCaseItem):
        self.session.delete(f"{self.api_url}/v1/processing-case-items/{instance.uuid}/")

    def filter(
        self,
        filters: ProcessingCaseItemFilters,
    ) -> List[ProcessingCaseItem]:
        response = self.session.get(f"{self.api_url}/v1/processing-case-items/")
        if response.status_code == 200:
            raw_response = response.json()
            return [
                ProcessingCaseItem.from_dict(camel_to_snake(item_data))
                for item_data in raw_response.get('data', [])
            ]
        return []
    
    def filter_with_tenant(
        self,
        tenant_slug: str,
        filters: ProcessingCaseItemFilters,
    ) -> List[ProcessingCaseItem]:
        response = self.session.get(f"{self.api_url}/v1/processing-case-items/")
        if response.status_code == 200:
            raw_response = response.json()
            return [
                ProcessingCaseItem.from_dict(camel_to_snake(item_data))
                for item_data in raw_response.get('data', [])
            ]
        return []

    @classmethod
    def _build_processing_case_item(cls, response: Response) -> ProcessingCaseItem:
        response_json = response.json()
        instance_data = response_json.get('data', {})
        return ProcessingCaseItem.from_dict(camel_to_snake(instance_data))
