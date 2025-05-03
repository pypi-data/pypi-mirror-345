from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class JobOrdersLabelsCreateResponse(BaseModel):
    accountId: UUID
    transactionId: Optional[str] = None
    shipmentId: str
