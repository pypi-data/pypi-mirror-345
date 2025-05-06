# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MetadataGetDistributionsResponse", "TagsSchema"]


class TagsSchema(BaseModel):
    description: str

    name: str

    output_type: str

    available_values: Optional[List[str]] = None

    created_at: Optional[datetime] = None

    date_format: Optional[str] = None

    examples: Optional[List[Union[str, Dict[str, object]]]] = None

    max_values: Union[int, str, List[object], None] = FieldInfo(alias="maxValues", default=None)

    neg_examples: Optional[List[str]] = None

    retry_feedback: Optional[Dict[str, object]] = None

    tag_id: Optional[str] = None

    tuned: Optional[int] = None

    updated_at: Optional[datetime] = None

    username: Optional[str] = None


class MetadataGetDistributionsResponse(BaseModel):
    count_distribution: Dict[str, Dict[str, object]]

    tags_schemas: List[TagsSchema]
