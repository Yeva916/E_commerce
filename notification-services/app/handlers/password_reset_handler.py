from contracts.events.auth import PasswordResetEvent
from app.services.notification_service import NotificationService
class PasswordResetHandler:
    def __init__(self,notification_service:NotificationService):
        self.notification_service = notification_service
    async def handle(self, 
                     event:PasswordResetEvent):
        await self.notification_service.send_password_reset_email(
            event=event
        )