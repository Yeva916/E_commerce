from app.services.template_service import TemplateService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from fastapi import Depends
from app.dispatcher.event_dispatcher import EventDispatcher
from app.handlers.user_registered_handler import UserRegisteredHandler
from app.handlers.password_reset_handler import PasswordResetHandler
from app.handlers.order_created_handler import OrderCreatedHandler
from contracts.events.event_types import EventType
def get_template_service()->TemplateService:
    return TemplateService()

def get_email_service()->EmailService:
    return EmailService()


def get_notification_service(
        email_service:EmailService=Depends(get_email_service),
        template_service:TemplateService=Depends(get_template_service)
)->NotificationService:
    return NotificationService(email_service,template_service)

def get_event_dispatcher(
        notification_service:NotificationService=Depends(get_notification_service)
)->EventDispatcher:
    handler = {
        EventType.USER_REGISTERED: UserRegisteredHandler(notification_service),
        # EventType.PASSWORD_RESET: PasswordResetHandler(notification_service),
        # EventType.ORDER_CREATED: OrderCreatedHandler(notification_service),
    }
    return EventDispatcher(handlers=handler)