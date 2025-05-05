from dataclasses import dataclass
from typing import Optional


@dataclass
class ScalingRequirements(object):
    documents: Optional[int] = 0
    processing_cases: Optional[int] = 0
    processing_case_items: Optional[int] = 0

    @property
    def to_dict(self):
        return {
            "documents": self.documents,
            "processing_cases": self.processing_cases,
            "processing_case_items": self.processing_case_items,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScalingRequirements":
        return cls(
            documents=data.get("documents", 0),
            processing_cases=data.get("processing_cases", 0),
            processing_case_items=data.get("processing_case_items", 0),
        )
