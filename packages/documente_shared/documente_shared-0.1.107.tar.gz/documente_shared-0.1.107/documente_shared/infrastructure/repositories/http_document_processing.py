from dataclasses import dataclass
from typing import List, Optional
from requests import Response

from documente_shared.application.payloads import camel_to_snake
from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.enums.document import DocumentProcessingStatus, DocumentProcessingCategory
from documente_shared.domain.repositories.document import DocumentProcessingRepository
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpDocumentProcessingRepository(
    DocumenteClientMixin,
    DocumentProcessingRepository,
):
    def find(self, digest: str) -> Optional[DocumentProcessing]:
        response = self.session.get(f"{self.api_url}/documents/{digest}/")
        if response.status_code == 200:
            return self._build_processing_case(response)
        return None

    def persist(self, instance: DocumentProcessing) -> DocumentProcessing:
        response = self.session.put(
            url=f"{self.api_url}/documents/{instance.digest}/",
            json=instance.to_simple_dict,
        )
        if response.status_code in [200, 201]:
            raise Exception(f'Error persisting document processing: {response.text}')
        return self._build_processing_case(response)
    
    def remove(self, instance: DocumentProcessing):
        self.session.delete(f"{self.api_url}/documents/{instance.digest}/")
        
    def filter(self, statuses: List[DocumentProcessingStatus]) -> List[DocumentProcessing]:
        response = self.session.get(f"{self.api_url}/documents/?statuses={statuses}")
        if response.status_code == 200:
            raw_response = response.json()
            return [
                DocumentProcessing.from_dict(camel_to_snake(item['documentProcessing']))
                for item in raw_response.get('data', [])
            ]
        return []
    
    @classmethod
    def _build_processing_case(cls, response: Response) -> DocumentProcessing:
        response_json = response.json()
        instance_data = response_json.get('data', {})
        return DocumentProcessing.from_dict(camel_to_snake(instance_data))
    
    