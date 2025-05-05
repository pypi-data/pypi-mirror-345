# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Required, TypedDict

__all__ = [
    "MetadataUpsertParams",
    "MetadataMetadataItem",
    "MetadataMetadataItemChunkLevel",
    "MetadataMetadataItemFileLevel",
]


class MetadataUpsertParams(TypedDict, total=False):
    metadata: Required[Dict[str, Dict[str, MetadataMetadataItem]]]

    data_connector_name: Optional[str]

    dataslice_id: Optional[str]


class MetadataMetadataItemChunkLevel(TypedDict, total=False):
    values: Required[List[str]]

    evidence: Optional[str]


class MetadataMetadataItemFileLevel(TypedDict, total=False):
    values: Required[List[str]]

    evidence: Optional[str]


class MetadataMetadataItem(TypedDict, total=False):
    chunk_level: Optional[Dict[str, Optional[MetadataMetadataItemChunkLevel]]]

    file_level: Optional[MetadataMetadataItemFileLevel]
