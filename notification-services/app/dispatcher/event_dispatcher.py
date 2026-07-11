# from shared.events.event_types import EventType

# from app.handlers.user_registered_handler import UserRegisteredHandler
# from app.handlers.password_reset_handler import PasswordResetHandler
# from app.handlers.order_created_handler import OrderCreatedHandler


class EventDispatcher:
    def __init__(self,handlers:dict=None):
        self.handlers=handlers or {}
    
    async def dispatch(self,event):
        
        handler = self.handlers.get(
            event.event_type
        )
        if handler is None:
            raise ValueError(
                f"No handler for {event.event_type}"
            )

        await handler.handle(event)