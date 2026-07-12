from app.services.notification_service import NotificationService
from contracts.events.order import OrderCreatedEvent
class OrderCreatedHandler:
        def __init__(self,notification_service:NotificationService):
            self.notification_service = notification_service

        async def handle(
                self,
                event:OrderCreatedEvent
        ):
            await self.notification_service.send_order_confirmation_email(
                 event=event
            )
            