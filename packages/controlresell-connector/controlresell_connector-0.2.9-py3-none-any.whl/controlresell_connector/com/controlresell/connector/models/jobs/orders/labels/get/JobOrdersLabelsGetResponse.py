from pydantic import BaseModel
from uuid import UUID

class JobOrdersLabelsGetResponse(BaseModel):
    accountId: UUID
    orderId: str
    labelUrl: str
