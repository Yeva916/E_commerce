class OrderCreatedHandler:

    async def handle(self, event):

        print(
            f"Order confirmation {event.order_id}"
        )