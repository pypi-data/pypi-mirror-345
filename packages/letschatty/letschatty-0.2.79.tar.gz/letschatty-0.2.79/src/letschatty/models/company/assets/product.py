from ...base_models.chatty_asset_model import CompanyAssetModel, ChattyAssetPreview
from typing import Dict, Any, Optional
from pydantic import Field, field_validator
import pycountry

class Product(CompanyAssetModel):
    name: str
    price: Optional[Dict[str, float]] = Field(default=None)
    information: Optional[str] = Field(default=None)
    parameters: Optional[Dict[str, Any]] = Field(default=None)
    external_id: Optional[str] = Field(default=None)

    @field_validator('price', mode='before')
    def validate_price(cls, v: Dict[str, float]):
        if v is None:
            return v
        for currency, amount in v.items():
            try:
                pycountry.currencies.get(alpha_3=currency)
            except KeyError:
                raise ValueError(f"Invalid currency code: {currency}. Must be a valid ISO 4217 currency code.")
            if amount < 0:
                raise ValueError(f"Price amount must be non-negative for currency {currency}")

        return v

    def get_preview(self) -> ChattyAssetPreview:
        return ChattyAssetPreview(id=self.id, name=self.name, created_at=self.created_at, company_id=self.company_id)