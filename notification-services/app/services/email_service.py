from .template_service import EmailTemplate

class EmailService:
    async def send(
        self,
        recipient,
        template:EmailTemplate
    ):  
        print(f"sending email to {recipient} subject:{template.subject}")
