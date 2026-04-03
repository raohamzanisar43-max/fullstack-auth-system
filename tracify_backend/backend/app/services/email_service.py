"""
Email service for sending emails (placeholder implementation)
"""

import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        
        if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
            logger.warning("Email service not configured. Skipping email send.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_username
            message["To"] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=self.smtp_tls,
                username=self.smtp_username,
                password=self.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        
        # Create reset link (adjust frontend URL as needed)
        reset_link = f"https://your-frontend.com/reset-password?token={reset_token}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
                <p style="color: #666; line-height: 1.6;">
                    You requested a password reset for your Tracerfy account. Click the button below to reset your password:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ reset_link }}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; line-height: 1.6;">
                    If you didn't request this password reset, you can safely ignore this email. The link will expire in 1 hour.
                </p>
                <p style="color: #666; line-height: 1.6;">
                    Alternatively, you can copy and paste this link into your browser:
                </p>
                <p style="background-color: #e9ecef; padding: 10px; word-break: break-all; color: #495057;">
                    {{ reset_link }}
                </p>
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                <p style="color: #6c757d; font-size: 12px; text-align: center;">
                    This is an automated message from Tracerfy. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        You requested a password reset for your Tracerfy account. Visit this link to reset your password:
        {reset_link}
        
        If you didn't request this password reset, you can safely ignore this email. The link will expire in 1 hour.
        
        This is an automated message from Tracerfy. Please do not reply to this email.
        """
        
        # Render template
        template = Template(html_template)
        html_content = template.render(reset_link=reset_link)
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset Your Tracerfy Password",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """Send email verification email"""
        
        # Create verification link
        verification_link = f"https://your-frontend.com/verify-email?token={verification_token}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                <h2 style="color: #333; text-align: center;">Verify Your Email Address</h2>
                <p style="color: #666; line-height: 1.6;">
                    Thank you for signing up for Tracerfy! Please verify your email address by clicking the button below:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ verification_link }}" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p style="color: #666; line-height: 1.6;">
                    If you didn't create an account with Tracerfy, you can safely ignore this email.
                </p>
                <p style="color: #666; line-height: 1.6;">
                    Alternatively, you can copy and paste this link into your browser:
                </p>
                <p style="background-color: #e9ecef; padding: 10px; word-break: break-all; color: #495057;">
                    {{ verification_link }}
                </p>
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                <p style="color: #6c757d; font-size: 12px; text-align: center;">
                    This is an automated message from Tracerfy. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Email Verification
        
        Thank you for signing up for Tracerfy! Please verify your email address by visiting this link:
        {verification_link}
        
        If you didn't create an account with Tracerfy, you can safely ignore this email.
        
        This is an automated message from Tracerfy. Please do not reply to this email.
        """
        
        # Render template
        template = Template(html_template)
        html_content = template.render(verification_link=verification_link)
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify Your Tracerfy Email Address",
            html_content=html_content,
            text_content=text_content
        )


# Global email service instance
email_service = EmailService()
