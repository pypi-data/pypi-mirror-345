from dataclasses import dataclass
from datetime import datetime, tzinfo
from decimal import Decimal
from typing import Optional, List

from documente_shared.application.time_utils import get_datetime_from_data
from documente_shared.domain.constants import la_paz_tz
from documente_shared.domain.entities.in_memory_document import InMemoryDocument
from documente_shared.domain.enums.common import ProcessingStatus, ProcessingSource
from documente_shared.domain.enums.processing_case import ProcessingDocumentType


@dataclass
class ProcessingCaseItem(object):
    uuid: str
    case_id: str
    digest: str
    status: ProcessingStatus
    document: InMemoryDocument
    document_type: Optional[ProcessingDocumentType] = None
    uploaded_from: Optional[ProcessingSource] = None
    processed_csv: Optional[InMemoryDocument] = None
    processed_xlsx: Optional[InMemoryDocument] = None
    processed_json: Optional[InMemoryDocument] = None
    processing_time: Optional[Decimal] = None
    processing_confidence: Optional[Decimal] = None
    uploaded_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    feedback: Optional[list | dict] = None
    metadata: Optional[dict] = None

    def __post_init__(self):
        self.feedback = self.feedback or []
        self.metadata = self.metadata or {}

    @property
    def has_processed_csv(self) -> bool:
        return self.processed_csv and self.processed_csv.is_valid

    @property
    def has_processed_xlsx(self) -> bool:
        return self.processed_xlsx and self.processed_xlsx.is_valid

    @property
    def has_processed_json(self) -> bool:
        return self.processed_json and self.processed_json.is_valid
    
    @property
    def is_procesable(self) -> bool:
        return (
            (self.status.is_pending or self.status.is_enqueued)
            and self.digest
            and self.document
            and self.document.is_procesable
        )

    @property
    def is_finished(self) -> bool:
        return self.status in [
            ProcessingStatus.COMPLETED,
            ProcessingStatus.FAILED,
        ]

    def pending(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.PENDING
        self.started_at = None

    def processing(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.PROCESSING
        self.started_at = datetime.now(tz=timezone)

    def failed(
        self,
        error_message: Optional[str] = None,
        timezone: tzinfo = la_paz_tz,
    ):
        self.status = ProcessingStatus.FAILED
        self.failed_at = datetime.now(tz=timezone)

    def completed(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.COMPLETED
        self.completed_at = datetime.now(tz=timezone)

    def incomplete(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.INCOMPLETE
        self.completed_at = datetime.now(tz=timezone)

    def deleted(self):
        self.status = ProcessingStatus.DELETED
    
    def in_review(self):
        self.status = ProcessingStatus.IN_REVIEW

    def __eq__(self, other: 'ProcessingCaseItem') -> bool:
        if not other:
            return False

        return (
            self.uuid == other.uuid
            and self.digest == other.digest
            and self.status == other.status
            and self.document_type == other.document_type
            and self.document == other.document
            and self.processing_time == other.processing_time
            and self.processing_confidence == other.processing_confidence
            and self.uploaded_at == other.uploaded_at
            and self.started_at == other.started_at
            and self.failed_at == other.failed_at
            and self.completed_at == other.completed_at
        )

    @property
    def to_dict(self) -> dict:
        return {
            'uuid': self.uuid,
            'case_id': self.case_id,
            'digest': self.digest,
            'status': str(self.status),
            'document':(
                self.document.to_dict
                if self.document else None
            ),
            'document_type': (
                str(self.document_type)
                if self.document_type else None
            ),
            'uploaded_from': (
                str(self.uploaded_from)
                if self.uploaded_from else None
            ),
            'processed_csv': (
                self.processed_csv.to_dict
                if self.processed_csv else None
            ),
            'processed_xlsx': (
                self.processed_xlsx.to_dict
                if self.processed_xlsx else None
            ),
            'processed_json': (
                self.processed_json.to_dict
                if self.processed_json else None
            ),
            'processing_time': (
                str(self.processing_time.quantize(Decimal('0.001')))
                if self.processing_time else None
            ),
            'processing_confidence': (
                str(self.processing_confidence.quantize(Decimal('0.001')))
                if self.processing_confidence else None
            ),
            'uploaded_at': (
                self.uploaded_at.isoformat()
                if self.uploaded_at else None
            ),
            'started_at': (
                self.started_at.isoformat()
                if self.started_at else None
            ),
            'failed_at': (
                self.failed_at.isoformat()
                if self.failed_at else None
            ),
            'feedback': self.feedback,
            'metadata': self.metadata,
            'completed_at': (
                self.completed_at.isoformat()
                if self.completed_at else None
            ),
        }

    @property
    def to_simple_dict(self) -> dict:
        simple_dict = self.to_dict.copy()
        return simple_dict

    @property
    def to_persist_dict(self) -> dict:
        simple_dict = self.to_dict.copy()
        simple_dict["document_path"] = self.document.file_path if self.document else None
        simple_dict["processed_csv_path"] = self.processed_csv.file_path if self.processed_csv else None
        simple_dict["processed_xlsx_path"] = self.processed_xlsx.file_path if self.processed_xlsx else None
        simple_dict["processed_json_path"] = self.processed_json.file_path if self.processed_json else None
        return simple_dict

    def overload(
        self,
        new_instance: 'ProcessingCaseItem',
        properties: List[str] = None,
    ):
        instance_properties = properties or [
            'status',
            'document',
            'document_type',
            'uploaded_from',
            'processed_csv',
            'processed_xlsx',
            'processed_json',
            'processing_time',
            'processing_confidence',
            'uploaded_at',
            'started_at',
            'failed_at',
            'completed_at',
            'feedback',
            'metadata',
        ]
        for _property in instance_properties:
            property_value = getattr(new_instance, _property)
            if not hasattr(self, _property):
                continue
            setattr(self, _property, property_value)
        return self

    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessingCaseItem':
        return cls(
            uuid=data.get('uuid'),
            case_id=data.get('case_id'),
            digest=data.get('digest'),
            status=ProcessingStatus.from_value(data.get('status')),
            document=(
                InMemoryDocument.from_dict(data.get('document'))
                if data.get('document') else None
            ),
            document_type=(
                ProcessingDocumentType.from_value(data.get('document_type'))
                if data.get('document_type') else None
            ),
            uploaded_from=(
                ProcessingSource.from_value(data.get('uploaded_from'))
                if data.get('uploaded_from') else None
            ),
            processed_csv=(
                InMemoryDocument.from_dict(data.get('processed_csv'))
                if data.get('processed_csv') else None
            ),
            processed_xlsx=(
                InMemoryDocument.from_dict(data.get('processed_xlsx'))
                if data.get('processed_xlsx') else None
            ),
            processed_json=(
                InMemoryDocument.from_dict(data.get('processed_json'))
                if data.get('processed_json') else None
            ),
            processing_time=(
                Decimal(data.get('processing_time'))
                if data.get('processing_time') else None
            ),
            processing_confidence=(
                Decimal(data.get('processing_confidence'))
                if data.get('processing_confidence') else None
            ),
            uploaded_at=get_datetime_from_data(input_datetime=data.get('uploaded_at')),
            started_at=get_datetime_from_data(input_datetime=data.get('started_at')),
            failed_at=get_datetime_from_data(input_datetime=data.get('failed_at')),
            feedback=data.get('feedback'),
            metadata=data.get('metadata', {}),
            completed_at=get_datetime_from_data(input_datetime=data.get('completed_at')),
        )

    @classmethod
    def from_persist_dict(cls, data: dict) -> 'ProcessingCaseItem':
        instance = cls.from_dict(data)
        if "document_path" in data:
            instance.document = InMemoryDocument(file_path=data["document_path"])
        if "processed_csv_path" in data:
            instance.processed_csv = InMemoryDocument(file_path=data["processed_csv_path"])
        if "processed_xlsx_path" in data:
            instance.processed_xlsx = InMemoryDocument(file_path=data["processed_xlsx_path"])
        if "processed_json_path" in data:
            instance.processed_json = InMemoryDocument(file_path=data["processed_json_path"])
        return instance
