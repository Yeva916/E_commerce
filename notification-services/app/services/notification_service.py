from .email_service import EmailService
from .template_service import TemplateService
from contracts.events.auth import UserRegisteredEvent,PasswordResetEvent
from contracts.events.order import OrderCreatedEvent
from app.core.config import settings

class NotificationService:
    def __init__(self,
                 email_service:EmailService,
                 template_service:TemplateService):
        self.email_service = email_service
        self.template_service = template_service

    
    async def send_verification_email(self,event:UserRegisteredEvent):
        print("helloo")
        verification_url = f"{settings.auth_service_url}/verify-email?token={event.verification_token}"
        template = self.template_service.verification_email(
            verification_url
        )
        await self.email_service.send(
            recipient=event.email,
            template=template
        )
        
    
    async def send_password_reset_email(self,event:PasswordResetEvent):
        reset_url = f"{settings.auth_service_url}/reset-password?token={event.reset_token}"
        template = self.template_service.password_reset_email(
            reset_url
        )
        await self.email_service.send(
            recipient=event.email,
            template=template
        )
    
    async def send_order_confirmation_email(self,event:OrderCreatedEvent):

        template = self.template_service.order_confirmation(
            event.order_id,
            total=event.total_amount
        )
        await self.email_service.send(
            recipient=event.email,
            template=template
        )