from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class JobOrdersLabelsGetPayload(BaseModel):
    accountId: UUID
    orderId: str
    transactionId: Optional[str] = None
    conversationId: Optional[str] = None
    shipmentId: Optional[str] = None
