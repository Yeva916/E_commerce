class PasswordResetHandler:

    async def handle(self, event):

        print(
            f"Reset email for {event.email}"
        )