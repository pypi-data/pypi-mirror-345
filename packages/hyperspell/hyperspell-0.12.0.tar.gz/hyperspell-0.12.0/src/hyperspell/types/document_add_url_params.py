# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["DocumentAddURLParams"]


class DocumentAddURLParams(TypedDict, total=False):
    url: Required[str]
    """Source URL of the document."""

    collection: Optional[str]
    """Name of the collection to add the document to.

    If the collection does not exist, it will be created. If not given, the document
    will be added to the user's default collection.
    """
