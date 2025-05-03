from pydantic import BaseModel
from typing import Optional

class JobPost(BaseModel):
    brand: str
    catalogId: int
    colorIds: Optional[list[int]] = None
    description: str
    measurementLength: Optional[float] = None
    measurementWidth: Optional[float] = None
    packageSizeId: int
    photoUrls: list[str]
    price: float
    sizeId: Optional[int] = None
    statusId: int
    title: str
    isDraft: bool
    material: Optional[list[int]] = None
    manufacturerLabelling: Optional[str] = None
