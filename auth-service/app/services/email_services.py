import httpx
from app.core.config import settings

class AsyncEmailService:
    def __init__(self,client:httpx.AsyncClient):
        self.client = client
        self.api_url = "https://api.resend.com/emails"
        self.headers = {
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json"
        }
    
    async def send(self,payload,):
        try:
            response =await self.client.post(self.api_url,
                                             json=payload,
                                             headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to send verification email: {e}")
    
    async def send_verification_email(self,to_email:str,verification_token:str):
        verification_link = f"{settings.base_url}/verify-email?token={verification_token}"
        html_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                        <h2>Welcome to our E-commerce Store!</h2>
                        <p>Thank you for signing up. Please verify your email address to unlock your account and begin shopping.</p>
                        <div style="margin: 30px 0;">
                            <a href="{verification_link}" 
                            style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                Verify Email Address
                            </a>
                        </div>
                        <p style="font-size: 12px; color: #666;">This verification link will expire in 15 minutes.</p>
                        <p style="font-size: 12px; color: #666;">If the button above doesn't work, copy and paste this URL into your browser:</p>
                        <p style="font-size: 12px; color: #0066cc;">{verification_link}</p>
                    </body>
                </html>
                """
        
        payload = {
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": "Activate Your Account",
            "html": html_content
        }
        return await self.send(payload)

    async def send_password_reset_email(self,to_email:str, reset_token:str):
        reset_link = f"{settings.base_url}/reset-password?token={reset_token}"
        html_content = f"""
                <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                            <h2>Password Reset Request</h2>
                            <p>We received a request to reset your password. Click the button below to proceed.</p>
                            <div style="margin: 30px 0;">
                                <a href="{reset_link}" 
                                style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                    Reset Password
                                </a>
                            </div>
                            <p style="font-size: 12px; color: #666;">This password reset link will expire in 15 minutes.</p>
                            <p style="font-size: 12px; color: #0066cc;">If the button above doesn't work, copy and paste this URL into your browser:</p>
                            <p style="font-size: 12px; color: #0066cc;">{reset_link}</p>
                        </body>
                    </html>
                    """
        payload = {
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": "Reset Your Password",
            "html": html_content
        }
        return await self.send(payload)
        