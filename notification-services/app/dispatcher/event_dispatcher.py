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