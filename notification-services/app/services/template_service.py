from pathlib import Path
from jinja2 import Environment,FileSystemLoader,select_autoescape

from dataclasses import dataclass

@dataclass(slots=True)
class EmailTemplate:
    subject: str
    html: str
    text: str | None = None

class TemplateService:
    def __init__(self):
        template_path = Path(__file__).parent.parent/"templates"
    
        self.environment = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html"])
            )
    
    def render(
            self,
            template_name:str,
            **context
    ):
        template = self.environment.get_template(template_name)
        return template.render(**context)
    
    def verification_email(
            self,
            verification_url
    ):  
        html = self.render("verify_email.html",
                           verification_url=verification_url)
        return EmailTemplate(
        subject="Verify your email",
        html=html,
        text=f"Verify your email by clicking the link.{verification_url}"
    ) 

    def password_reset_email(
            self,
            reset_url,
    ):
        html = self.render(
        "password_reset.html",
        reset_url=reset_url,
    )
        return EmailTemplate(
        subject="Password Reset Email",
        html=html,
        text=f"Reset your password.{reset_url}"
    ) 

    def order_confirmation(
            self,
            order_number,
            total,
        ):
        html = self.render(
        "order_confirmation.html",
        order_number=order_number,
        total_amount=total,
    )
        return EmailTemplate(
        subject="Order confirmation email",
        html=html,
        text=f"Your order has been confirmed order_id:{order_number},total_amount:{total}"
    ) 