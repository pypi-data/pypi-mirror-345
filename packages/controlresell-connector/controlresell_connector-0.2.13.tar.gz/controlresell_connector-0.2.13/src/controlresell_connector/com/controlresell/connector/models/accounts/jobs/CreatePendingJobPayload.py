from pydantic import BaseModel
from controlresell_connector.com.controlresell.connector.models.application.RabbitMQRoutingKey import RabbitMQRoutingKey

class CreatePendingJobPayload(BaseModel):
    routingKey: RabbitMQRoutingKey
    payload: str
