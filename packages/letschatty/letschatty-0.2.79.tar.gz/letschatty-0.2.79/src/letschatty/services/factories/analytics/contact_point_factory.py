from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from ....models.company.assets.contact_point import ContactPoint

if TYPE_CHECKING:
    from ....models.analytics.sources import Source

logger = logging.getLogger(__name__)

class ContactPointFactory:

    @staticmethod
    def instantiate_contact_point(data: dict, source: Source) -> ContactPoint:
        contact_point = ContactPoint(**data)
        contact_point.source = source
        return contact_point