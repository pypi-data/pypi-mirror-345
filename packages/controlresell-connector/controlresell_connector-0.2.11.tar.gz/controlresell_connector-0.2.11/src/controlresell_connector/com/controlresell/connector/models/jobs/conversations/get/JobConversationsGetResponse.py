from pydantic import BaseModel
from controlresell_connector.com.controlresell.connector.models.jobs.conversations.JobConversation import JobConversation
from controlresell_connector.com.controlresell.connector.models.jobs.orders.JobOrder import JobOrder
from typing import Optional
from controlresell_connector.com.controlresell.connector.models.jobs.orders.labels.get.JobOrdersLabelsGetResponse import JobOrdersLabelsGetResponse

class JobConversationsGetResponse(BaseModel):
    conversation: JobConversation
    orders: Optional[list[JobOrder]] = None
    labels: Optional[list[JobOrdersLabelsGetResponse]] = None
