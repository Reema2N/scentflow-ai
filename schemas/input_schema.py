from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class FragranceNotes(BaseModel):
    top_notes: List[str] = Field(
        description="Top notes of the perfume."
    )

    middle_notes: List[str] = Field(
        description="Middle or heart notes of the perfume."
    )

    base_notes: List[str] = Field(
        description="Base notes of the perfume."
    )


class ProductInput(BaseModel):
    name: str = Field(
        min_length=1,
        description="Name of the perfume."
    )

    fragrance_notes: FragranceNotes

    description: Optional[str] = Field(
        default=None,
        description="Optional product description provided by the client."
    )


class CampaignInput(BaseModel):
    occasion: str = Field(
        min_length=1,
        description="Campaign occasion or event, such as Saudi National Day."
    )

    channels: List[Literal["Instagram", "Email"]] = Field(
    min_length=1,
    description="Marketing channels requested by the client."
    )


class BrandInput(BaseModel):
    colors: Optional[List[str]] = Field(
        default=None,
        description="Brand colors provided by the client."
    )


class UserInput(BaseModel):
    product: ProductInput
    campaign: CampaignInput
    brand: BrandInput = Field(
        default_factory=BrandInput
    )