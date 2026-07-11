from contracts.events.auth import UserRegisteredEvent
from app.services.notification_service import NotificationService

class UserRegisteredHandler:
    def __init__(self,notification_service:NotificationService):
        self.notification_service = notification_service

    async def handle(
        self,
        event: UserRegisteredEvent,
    ):

        print("inside_handler",event.email)
        print(self.notification_service)
        print(type(self.notification_service))
        await self.notification_service.send_verification_email(
            event=event
        )
