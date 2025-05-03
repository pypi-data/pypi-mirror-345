import base64
from typing import Optional
from dataclasses import dataclass

from documente_shared.application.files import (
    remove_slash_from_path,
    get_filename_from_path,
)
from documente_shared.domain.exceptions import InMemoryDocumentContentError


@dataclass
class InMemoryDocument(object):
    file_path: Optional[str] = None
    file_bytes: Optional[bytes] = None
    file_base64: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.file_path) and self.file_bytes

    @property
    def has_content(self) -> bool:
        return bool(self.file_bytes) or bool(self.file_base64)

    @property
    def file_name(self) -> Optional[str]:
        if not self.file_path:
            return None
        return get_filename_from_path(self.file_path)

    @property
    def file_key(self) -> Optional[str]:
        return self.file_name

    @property
    def is_procesable(self) -> bool:
        return self.is_valid and self.has_content

    @property
    def to_dict(self) -> dict:
        data = dict()
        if self.file_path:
            data['file_path'] = remove_slash_from_path(self.file_path)
        if self.file_bytes:
            data['file_bytes'] = self.file_bytes.decode('utf-8')
        if self.file_base64:
            data['file_base64'] = self.file_base64
        return data

    @classmethod
    def from_dict(cls, data: dict):
        has_bytes_content = data.get('file_bytes') and isinstance(data['file_bytes'], bytes)
        has_base64_content = data.get('file_base64') and isinstance(data['file_base64'], str)

        if not has_bytes_content and not has_base64_content:
            raise InMemoryDocumentContentError

        if has_bytes_content and not data.get('file_base64'):
            data['file_base64'] = base64.b64encode(data.get('file_bytes')).decode("utf-8")

        if has_base64_content and not data.get('file_bytes'):
            data['file_bytes'] = base64.b64decode(data.get('file_base64'))

        return cls(
            file_path=data.get('file_path'),
            file_bytes=data.get('file_bytes'),
            file_base64=data.get('file_base64'),
        )
