from contracts.events.event_types import EventType
from app.dispatcher.event_dispatcher import EventDispatcher
from app.handlers.user_registered_handler import UserRegisteredHandler
from app.handlers.password_reset_handler import PasswordResetHandler
from app.handlers.order_created_handler import OrderCreatedHandler
from app.services.template_service import TemplateService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
class ConsumerContainer:
    def __init__(self,):
        #i can initialize the client here
        self.template_service = TemplateService()
        self.email_service = EmailService()
        self.notificaiton_service = NotificationService(
            email_service=self.email_service,
            template_service=self.template_service
        )
        handler = {
            EventType.USER_REGISTERED:UserRegisteredHandler(self.notificaiton_service),
            EventType.PASSWORD_RESET: PasswordResetHandler(self.notificaiton_service),
            EventType.ORDER_CREATED: OrderCreatedHandler(self.notificaiton_service),
        }
        self.event_dispatcher = EventDispatcher(handlers=handler)

container = ConsumerContainer()