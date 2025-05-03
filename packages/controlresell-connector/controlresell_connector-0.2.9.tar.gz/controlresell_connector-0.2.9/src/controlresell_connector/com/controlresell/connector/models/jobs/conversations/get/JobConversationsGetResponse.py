from pydantic import BaseModel
from controlresell_connector.com.controlresell.connector.models.jobs.conversations.JobConversation import JobConversation
from controlresell_connector.com.controlresell.connector.models.jobs.orders.labels.create.JobOrdersLabelsCreateResponse import JobOrdersLabelsCreateResponse
from typing import Optional
from controlresell_connector.com.controlresell.connector.models.jobs.orders.labels.get.JobOrdersLabelsGetResponse import JobOrdersLabelsGetResponse

class JobConversationsGetResponse(BaseModel):
    conversation: JobConversation
    ordersLabelsCreateResponse: Optional[JobOrdersLabelsCreateResponse] = None
    ordersLabelsGetResponse: Optional[JobOrdersLabelsGetResponse] = None
