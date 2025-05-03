from pydantic import BaseModel
from uuid import UUID
from controlresell_connector.com.controlresell.connector.models.application.RabbitMQRoutingKey import RabbitMQRoutingKey
from datetime import datetime

class PendingJob(BaseModel):
    id: UUID
    accountId: UUID
    routingKey: RabbitMQRoutingKey
    payload: str
    expiresAt: datetime
