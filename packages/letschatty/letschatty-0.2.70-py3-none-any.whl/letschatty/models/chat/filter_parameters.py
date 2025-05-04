from letschatty.models.utils.types import StrObjectId
from pydantic import BaseModel, Field
from letschatty.models.utils.definitions import Area
from letschatty.models.chat.quality_scoring import QualityScore
from datetime import datetime, timedelta

class FilterParameters(BaseModel):
    previews_per_page: int = Field(default=10, ge=1)
    order_desc: int = Field(default=1, ge=0, le=1)
    page_number: int = Field(default=1, ge=1)
    unread: int = Field(default=0, ge=0, le=1)
    starred: int = Field(default=0, ge=0, le=1)
    time_left_order: int = Field(default=0, ge=0, le=1)
    products: list[StrObjectId] = Field(default=[])
    sales_products: list[StrObjectId] = Field(default=[])
    tags: list[StrObjectId] = Field(default=[])
    search_like: str = Field(default="")
    agents: list[StrObjectId] = Field(default=[])
    business_areas: list[StrObjectId] = Field(default=[])
    funnels: list[StrObjectId] = Field(default=[])
    funnel_stages: list[StrObjectId] = Field(default=[])
    area_status: list[Area] = Field(default=[])
    time_since_last_message_hours: int = Field(default=0, ge=0)
    sources: list[StrObjectId] = Field(default=[])
    quality_score: list[QualityScore] = Field(default=[])
    messages_count: int = Field(default=0, ge=0)
    search_in_chat: str = Field(default="")
    workflows: list[StrObjectId] = Field(default=[])
    last_message_date_range: tuple[datetime, datetime] = Field(default=())
    sales_date_range: tuple[datetime, datetime] = Field(default=())
    sources_date_range: tuple[datetime, datetime] = Field(default=())
    sent_templates : list[str] = Field(default=[])
