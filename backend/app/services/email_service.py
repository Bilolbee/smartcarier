"""
=============================================================================
EMAIL SERVICE - SMTP & SendGrid Integration
=============================================================================

Bu service email yuborish uchun ishlatiladi:
- SMTP (Gmail, Outlook, etc.)
- SendGrid (Production uchun tavsiya)

Xususiyatlari:
- Async email yuborish
- HTML templates
- Queue orqali yuborish (Background Tasks)
- Retry mechanism
- Email logging

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import asyncio
import json

# For async email
import aiosmtplib

# For templates
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from pathlib import Path

from app.config import settings

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# EMAIL TYPES
# =============================================================================

class EmailType(str, Enum):
    """Email turlari."""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGED = "password_changed"
    LOGIN_NOTIFICATION = "login_notification"
    REGISTRATION_SUCCESS = "registration_success"
    EMAIL_VERIFICATION = "email_verification"
    PREMIUM_UPGRADE = "premium_upgrade"
    PREMIUM_EXPIRED = "premium_expired"
    APPLICATION_STATUS = "application_status"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    JOB_MATCH = "job_match"
    WEEKLY_DIGEST = "weekly_digest"


# =============================================================================
# EMAIL TEMPLATES
# =============================================================================

EMAIL_TEMPLATES = {
    EmailType.WELCOME: {
        "subject": "🎉 SmartCareer AI ga xush kelibsiz!",
        "subject_ru": "🎉 Добро пожаловать в SmartCareer AI!",
    },
    EmailType.PASSWORD_RESET: {
        "subject": "🔐 Parolni tiklash - SmartCareer AI",
        "subject_ru": "🔐 Сброс пароля - SmartCareer AI",
    },
    EmailType.PASSWORD_CHANGED: {
        "subject": "✅ Parol muvaffaqiyatli o'zgartirildi",
        "subject_ru": "✅ Пароль успешно изменен",
    },
    EmailType.LOGIN_NOTIFICATION: {
        "subject": "🔔 Yangi kirish aniqlandi - SmartCareer AI",
        "subject_ru": "🔔 Обнаружен новый вход - SmartCareer AI",
    },
    EmailType.REGISTRATION_SUCCESS: {
        "subject": "✅ Ro'yxatdan o'tish muvaffaqiyatli!",
        "subject_ru": "✅ Регистрация успешна!",
    },
    EmailType.EMAIL_VERIFICATION: {
        "subject": "📧 Email manzilingizni tasdiqlang",
        "subject_ru": "📧 Подтвердите ваш email",
    },
    EmailType.PREMIUM_UPGRADE: {
        "subject": "⭐ Premium ga o'tdingiz! - SmartCareer AI",
        "subject_ru": "⭐ Вы перешли на Premium! - SmartCareer AI",
    },
    EmailType.APPLICATION_STATUS: {
        "subject": "📋 Ariza holati yangilandi - SmartCareer AI",
        "subject_ru": "📋 Статус заявки обновлен - SmartCareer AI",
    },
    EmailType.INTERVIEW_SCHEDULED: {
        "subject": "📅 Suhbat belgilandi! - SmartCareer AI",
        "subject_ru": "📅 Собеседование назначено! - SmartCareer AI",
    },
}


# =============================================================================
# EMAIL SERVICE CLASS
# =============================================================================

class EmailService:
    """
    Email yuborish xizmati.
    
    SMTP va SendGrid ni qo'llab-quvvatlaydi.
    """
    
    def __init__(self):
        """Initialize email service."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from_email = settings.SMTP_FROM_EMAIL
        self.smtp_from_name = settings.SMTP_FROM_NAME
        self.smtp_use_tls = settings.SMTP_USE_TLS
        
        # SendGrid
        self.sendgrid_api_key = settings.SENDGRID_API_KEY
        self.use_sendgrid = bool(self.sendgrid_api_key)
        
        # Template engine
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        if template_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            self.jinja_env = None
            logger.warning(f"Email templates directory not found: {template_dir}")
        
        logger.info(f"EmailService initialized. SendGrid: {self.use_sendgrid}")
    
    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    
    async def send_email(
        self,
        to_email: str,
        email_type: EmailType,
        context: Dict[str, Any],
        language: str = "uz",
        to_name: Optional[str] = None,
    ) -> bool:
        """
        Email yuborish.
        
        Args:
            to_email: Qabul qiluvchi email
            email_type: Email turi
            context: Template uchun ma'lumotlar
            language: Til (uz, ru, en)
            to_name: Qabul qiluvchi ismi
            
        Returns:
            True agar muvaffaqiyatli, False aks holda
        """
        try:
            # Get subject
            template_config = EMAIL_TEMPLATES.get(email_type, {})
            subject = template_config.get(
                f"subject_{language}" if language != "uz" else "subject",
                template_config.get("subject", "SmartCareer AI")
            )
            
            # Render HTML body
            html_body = self._render_template(email_type, context, language)
            
            # Send via appropriate provider
            if self.use_sendgrid:
                success = await self._send_via_sendgrid(
                    to_email, to_name, subject, html_body
                )
            else:
                success = await self._send_via_smtp(
                    to_email, to_name, subject, html_body
                )
            
            # Log result
            if success:
                logger.info(f"Email sent successfully: {email_type.value} to {to_email[:3]}***")
            else:
                logger.error(f"Email failed: {email_type.value} to {to_email[:3]}***")
            
            return success
            
        except Exception as e:
            logger.exception(f"Email error: {e}")
            return False
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        language: str = "uz"
    ) -> bool:
        """Send welcome email after registration."""
        context = {
            "user_name": user_name,
            "login_url": f"{settings.FRONTEND_URL}/login",
            "dashboard_url": f"{settings.FRONTEND_URL}/student",
        }
        return await self.send_email(
            to_email, EmailType.WELCOME, context, language, user_name
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str,
        language: str = "uz"
    ) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        context = {
            "user_name": user_name,
            "reset_url": reset_url,
            "expires_in": "1 soat" if language == "uz" else "1 час",
        }
        return await self.send_email(
            to_email, EmailType.PASSWORD_RESET, context, language, user_name
        )
    
    async def send_password_changed_email(
        self,
        to_email: str,
        user_name: str,
        language: str = "uz"
    ) -> bool:
        """Send password changed notification."""
        context = {
            "user_name": user_name,
            "changed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "support_email": settings.SUPPORT_EMAIL,
        }
        return await self.send_email(
            to_email, EmailType.PASSWORD_CHANGED, context, language, user_name
        )
    
    async def send_login_notification(
        self,
        to_email: str,
        user_name: str,
        ip_address: str,
        user_agent: str,
        language: str = "uz"
    ) -> bool:
        """Send login notification email."""
        context = {
            "user_name": user_name,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "login_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "security_url": f"{settings.FRONTEND_URL}/settings/security",
        }
        return await self.send_email(
            to_email, EmailType.LOGIN_NOTIFICATION, context, language, user_name
        )
    
    async def send_registration_success_email(
        self,
        to_email: str,
        user_name: str,
        role: str,
        language: str = "uz"
    ) -> bool:
        """Send registration success email."""
        dashboard_url = (
            f"{settings.FRONTEND_URL}/company" 
            if role == "company" 
            else f"{settings.FRONTEND_URL}/student"
        )
        context = {
            "user_name": user_name,
            "role": role,
            "dashboard_url": dashboard_url,
            "features": self._get_role_features(role, language),
        }
        return await self.send_email(
            to_email, EmailType.REGISTRATION_SUCCESS, context, language, user_name
        )
    
    async def send_email_verification(
        self,
        to_email: str,
        user_name: str,
        verification_token: str,
        language: str = "uz"
    ) -> bool:
        """Send email verification link."""
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        context = {
            "user_name": user_name,
            "verify_url": verify_url,
            "expires_in": "24 soat" if language == "uz" else "24 часа",
        }
        return await self.send_email(
            to_email, EmailType.EMAIL_VERIFICATION, context, language, user_name
        )
    
    async def send_application_status_email(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company_name: str,
        new_status: str,
        language: str = "uz"
    ) -> bool:
        """Send application status update email."""
        context = {
            "user_name": user_name,
            "job_title": job_title,
            "company_name": company_name,
            "new_status": new_status,
            "applications_url": f"{settings.FRONTEND_URL}/student/applications",
        }
        return await self.send_email(
            to_email, EmailType.APPLICATION_STATUS, context, language, user_name
        )
    
    async def send_interview_scheduled_email(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company_name: str,
        interview_date: str,
        interview_time: str,
        interview_type: str,  # video, phone, in-person
        meeting_link: Optional[str] = None,
        language: str = "uz"
    ) -> bool:
        """Send interview scheduled notification."""
        context = {
            "user_name": user_name,
            "job_title": job_title,
            "company_name": company_name,
            "interview_date": interview_date,
            "interview_time": interview_time,
            "interview_type": interview_type,
            "meeting_link": meeting_link,
        }
        return await self.send_email(
            to_email, EmailType.INTERVIEW_SCHEDULED, context, language, user_name
        )
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _render_template(
        self,
        email_type: EmailType,
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Render email template."""
        # Add common context
        context.update({
            "app_name": "SmartCareer AI",
            "app_url": settings.FRONTEND_URL,
            "support_email": settings.SUPPORT_EMAIL,
            "current_year": datetime.now().year,
            "language": language,
        })
        
        # Try to load template file
        if self.jinja_env:
            try:
                template_name = f"{email_type.value}_{language}.html"
                template = self.jinja_env.get_template(template_name)
                return template.render(**context)
            except Exception as e:
                logger.warning(f"Template not found: {template_name}, using default")
        
        # Fallback to inline template
        return self._get_default_template(email_type, context, language)
    
    def _get_default_template(
        self,
        email_type: EmailType,
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Get default inline HTML template."""
        user_name = context.get("user_name", "Foydalanuvchi")
        
        # Base HTML structure
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SmartCareer AI</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .button:hover {{ opacity: 0.9; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .info-box {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .warning-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 SmartCareer AI</h1>
                </div>
                <div class="content">
        """
        
        # Add content based on email type
        if email_type == EmailType.WELCOME:
            if language == "ru":
                html += f"""
                    <h2>Добро пожаловать, {user_name}! 🎉</h2>
                    <p>Спасибо за регистрацию в SmartCareer AI - платформе для карьеры нового поколения.</p>
                    <p>Теперь вы можете:</p>
                    <ul>
                        <li>✨ Создавать профессиональные резюме с помощью AI</li>
                        <li>🔍 Искать подходящие вакансии</li>
                        <li>📝 Подавать заявки одним кликом</li>
                        <li>📊 Отслеживать статус заявок</li>
                    </ul>
                    <a href="{context.get('dashboard_url', '#')}" class="button">Перейти в личный кабинет</a>
                """
            else:
                html += f"""
                    <h2>Xush kelibsiz, {user_name}! 🎉</h2>
                    <p>SmartCareer AI ga ro'yxatdan o'tganingiz uchun rahmat - yangi avlod karyera platformasi.</p>
                    <p>Endi siz quyidagilarni qilishingiz mumkin:</p>
                    <ul>
                        <li>✨ AI yordamida professional rezyume yaratish</li>
                        <li>🔍 O'zingizga mos ishlarni qidirish</li>
                        <li>📝 Bir marta bosish bilan ariza berish</li>
                        <li>📊 Arizalar holatini kuzatish</li>
                    </ul>
                    <a href="{context.get('dashboard_url', '#')}" class="button">Boshqaruv paneliga o'tish</a>
                """
        
        elif email_type == EmailType.PASSWORD_RESET:
            if language == "ru":
                html += f"""
                    <h2>Сброс пароля</h2>
                    <p>Здравствуйте, {user_name}!</p>
                    <p>Мы получили запрос на сброс пароля для вашего аккаунта.</p>
                    <a href="{context.get('reset_url', '#')}" class="button">Сбросить пароль</a>
                    <div class="warning-box">
                        <strong>⚠️ Важно:</strong> Ссылка действительна в течение {context.get('expires_in', '1 час')}.
                        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
                    </div>
                """
            else:
                html += f"""
                    <h2>Parolni tiklash</h2>
                    <p>Salom, {user_name}!</p>
                    <p>Hisobingiz uchun parolni tiklash so'rovi qabul qilindi.</p>
                    <a href="{context.get('reset_url', '#')}" class="button">Parolni tiklash</a>
                    <div class="warning-box">
                        <strong>⚠️ Muhim:</strong> Havola {context.get('expires_in', '1 soat')} davomida amal qiladi.
                        Agar siz parolni tiklashni so'ramagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring.
                    </div>
                """
        
        elif email_type == EmailType.PASSWORD_CHANGED:
            if language == "ru":
                html += f"""
                    <h2>Пароль изменен ✅</h2>
                    <p>Здравствуйте, {user_name}!</p>
                    <p>Пароль вашего аккаунта был успешно изменен.</p>
                    <div class="info-box">
                        <strong>🕐 Время изменения:</strong> {context.get('changed_at', 'Только что')}
                    </div>
                    <div class="warning-box">
                        <strong>⚠️ Не вы?</strong> Если вы не меняли пароль, немедленно свяжитесь с нами: {context.get('support_email', 'support@smartcareer.uz')}
                    </div>
                """
            else:
                html += f"""
                    <h2>Parol o'zgartirildi ✅</h2>
                    <p>Salom, {user_name}!</p>
                    <p>Hisobingiz paroli muvaffaqiyatli o'zgartirildi.</p>
                    <div class="info-box">
                        <strong>🕐 O'zgartirilgan vaqt:</strong> {context.get('changed_at', 'Hozirgina')}
                    </div>
                    <div class="warning-box">
                        <strong>⚠️ Bu siz emasmidingiz?</strong> Agar parolni o'zgartirmagan bo'lsangiz, darhol biz bilan bog'laning: {context.get('support_email', 'support@smartcareer.uz')}
                    </div>
                """
        
        elif email_type == EmailType.LOGIN_NOTIFICATION:
            if language == "ru":
                html += f"""
                    <h2>Новый вход в аккаунт 🔔</h2>
                    <p>Здравствуйте, {user_name}!</p>
                    <p>Обнаружен новый вход в ваш аккаунт:</p>
                    <div class="info-box">
                        <p><strong>🕐 Время:</strong> {context.get('login_time', 'Только что')}</p>
                        <p><strong>🌐 IP-адрес:</strong> {context.get('ip_address', 'Неизвестно')}</p>
                        <p><strong>💻 Устройство:</strong> {context.get('user_agent', 'Неизвестно')[:50]}...</p>
                    </div>
                    <div class="warning-box">
                        <strong>⚠️ Не вы?</strong> <a href="{context.get('security_url', '#')}">Проверьте настройки безопасности</a>
                    </div>
                """
            else:
                html += f"""
                    <h2>Hisobga yangi kirish 🔔</h2>
                    <p>Salom, {user_name}!</p>
                    <p>Hisobingizga yangi kirish aniqlandi:</p>
                    <div class="info-box">
                        <p><strong>🕐 Vaqt:</strong> {context.get('login_time', 'Hozirgina')}</p>
                        <p><strong>🌐 IP manzil:</strong> {context.get('ip_address', 'Noma\'lum')}</p>
                        <p><strong>💻 Qurilma:</strong> {context.get('user_agent', 'Noma\'lum')[:50]}...</p>
                    </div>
                    <div class="warning-box">
                        <strong>⚠️ Bu siz emasmidingiz?</strong> <a href="{context.get('security_url', '#')}">Xavfsizlik sozlamalarini tekshiring</a>
                    </div>
                """
        
        elif email_type == EmailType.APPLICATION_STATUS:
            status_colors = {
                "pending": "#f59e0b",
                "reviewing": "#3b82f6",
                "interview": "#8b5cf6",
                "accepted": "#10b981",
                "rejected": "#ef4444",
            }
            status_color = status_colors.get(context.get('new_status', '').lower(), '#666')
            
            if language == "ru":
                html += f"""
                    <h2>Статус заявки обновлен 📋</h2>
                    <p>Здравствуйте, {user_name}!</p>
                    <p>Статус вашей заявки на позицию <strong>{context.get('job_title', 'Вакансия')}</strong> в компании <strong>{context.get('company_name', 'Компания')}</strong> был обновлен:</p>
                    <div style="background: {status_color}; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <strong style="font-size: 18px;">{context.get('new_status', 'Обновлено').upper()}</strong>
                    </div>
                    <a href="{context.get('applications_url', '#')}" class="button">Посмотреть заявки</a>
                """
            else:
                html += f"""
                    <h2>Ariza holati yangilandi 📋</h2>
                    <p>Salom, {user_name}!</p>
                    <p><strong>{context.get('company_name', 'Kompaniya')}</strong> kompaniyasidagi <strong>{context.get('job_title', 'Vakansiya')}</strong> lavozimiga arizangiz holati yangilandi:</p>
                    <div style="background: {status_color}; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <strong style="font-size: 18px;">{context.get('new_status', 'Yangilandi').upper()}</strong>
                    </div>
                    <a href="{context.get('applications_url', '#')}" class="button">Arizalarni ko'rish</a>
                """
        
        elif email_type == EmailType.INTERVIEW_SCHEDULED:
            if language == "ru":
                html += f"""
                    <h2>Собеседование назначено! 📅</h2>
                    <p>Поздравляем, {user_name}! 🎉</p>
                    <p>Вы приглашены на собеседование на позицию <strong>{context.get('job_title', 'Вакансия')}</strong> в компании <strong>{context.get('company_name', 'Компания')}</strong>!</p>
                    <div class="info-box">
                        <p><strong>📅 Дата:</strong> {context.get('interview_date', 'TBD')}</p>
                        <p><strong>🕐 Время:</strong> {context.get('interview_time', 'TBD')}</p>
                        <p><strong>📍 Формат:</strong> {context.get('interview_type', 'Online')}</p>
                        {f'<p><strong>🔗 Ссылка:</strong> <a href="{context.get("meeting_link")}">{context.get("meeting_link")}</a></p>' if context.get('meeting_link') else ''}
                    </div>
                    <p>Удачи! 🍀</p>
                """
            else:
                html += f"""
                    <h2>Suhbat belgilandi! 📅</h2>
                    <p>Tabriklaymiz, {user_name}! 🎉</p>
                    <p>Siz <strong>{context.get('company_name', 'Kompaniya')}</strong> kompaniyasidagi <strong>{context.get('job_title', 'Vakansiya')}</strong> lavozimiga suhbatga taklif qilindingiz!</p>
                    <div class="info-box">
                        <p><strong>📅 Sana:</strong> {context.get('interview_date', 'Belgilanmagan')}</p>
                        <p><strong>🕐 Vaqt:</strong> {context.get('interview_time', 'Belgilanmagan')}</p>
                        <p><strong>📍 Format:</strong> {context.get('interview_type', 'Online')}</p>
                        {f'<p><strong>🔗 Havola:</strong> <a href="{context.get("meeting_link")}">{context.get("meeting_link")}</a></p>' if context.get('meeting_link') else ''}
                    </div>
                    <p>Omad tilaymiz! 🍀</p>
                """
        
        else:
            # Generic template
            html += f"""
                <h2>SmartCareer AI Bildirishnomasi</h2>
                <p>Salom, {user_name}!</p>
                <p>Sizga SmartCareer AI dan bildirishnoma keldi.</p>
            """
        
        # Close HTML
        html += f"""
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} SmartCareer AI. Barcha huquqlar himoyalangan.</p>
                    <p>
                        <a href="{settings.FRONTEND_URL}" style="color: #7c3aed;">Veb-sayt</a> |
                        <a href="{settings.FRONTEND_URL}/settings" style="color: #7c3aed;">Sozlamalar</a> |
                        <a href="mailto:{settings.SUPPORT_EMAIL}" style="color: #7c3aed;">Yordam</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_role_features(self, role: str, language: str) -> List[str]:
        """Get features list based on role."""
        if role == "company":
            if language == "ru":
                return [
                    "Публикация вакансий",
                    "AI-фильтрация кандидатов",
                    "Управление заявками",
                    "Планирование собеседований",
                ]
            return [
                "Vakansiyalar e'lon qilish",
                "AI yordamida nomzodlarni saralash",
                "Arizalarni boshqarish",
                "Suhbatlarni rejalashtirish",
            ]
        else:
            if language == "ru":
                return [
                    "AI-генерация резюме",
                    "Поиск вакансий",
                    "Автоматическая подача заявок",
                    "Отслеживание статуса",
                ]
            return [
                "AI bilan rezyume yaratish",
                "Ish qidirish",
                "Avtomatik ariza berish",
                "Holat kuzatish",
            ]
    
    async def _send_via_smtp(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        html_body: str
    ) -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            message["To"] = f"{to_name} <{to_email}>" if to_name else to_email
            
            # Attach HTML
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send async
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
            )
            
            return True
            
        except Exception as e:
            logger.exception(f"SMTP error: {e}")
            return False
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        html_body: str
    ) -> bool:
        """Send email via SendGrid API."""
        try:
            import httpx
            
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "personalizations": [{
                    "to": [{"email": to_email, "name": to_name or ""}],
                    "subject": subject,
                }],
                "from": {
                    "email": self.smtp_from_email,
                    "name": self.smtp_from_name,
                },
                "content": [{
                    "type": "text/html",
                    "value": html_body,
                }],
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                return response.status_code in (200, 202)
                
        except Exception as e:
            logger.exception(f"SendGrid error: {e}")
            return False


# =============================================================================
# EMAIL QUEUE (Background Tasks)
# =============================================================================

class EmailQueue:
    """
    Email queue for background sending.
    
    In production, use Celery + Redis.
    For development, uses asyncio.
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self._queue: List[Dict[str, Any]] = []
        self._is_processing = False
    
    async def enqueue(
        self,
        to_email: str,
        email_type: EmailType,
        context: Dict[str, Any],
        language: str = "uz",
        to_name: Optional[str] = None,
        priority: int = 5,  # 1 = highest, 10 = lowest
    ) -> str:
        """
        Add email to queue.
        
        Returns:
            Queue item ID
        """
        import uuid
        
        item_id = str(uuid.uuid4())
        
        self._queue.append({
            "id": item_id,
            "to_email": to_email,
            "email_type": email_type,
            "context": context,
            "language": language,
            "to_name": to_name,
            "priority": priority,
            "created_at": datetime.now(timezone.utc),
            "status": "pending",
            "attempts": 0,
        })
        
        # Sort by priority
        self._queue.sort(key=lambda x: x["priority"])
        
        logger.info(f"Email queued: {item_id} ({email_type.value})")
        
        # Start processing if not already
        if not self._is_processing:
            asyncio.create_task(self._process_queue())
        
        return item_id
    
    async def _process_queue(self):
        """Process queued emails."""
        self._is_processing = True
        
        while self._queue:
            item = self._queue.pop(0)
            
            try:
                success = await self.email_service.send_email(
                    to_email=item["to_email"],
                    email_type=item["email_type"],
                    context=item["context"],
                    language=item["language"],
                    to_name=item["to_name"],
                )
                
                if not success and item["attempts"] < 3:
                    # Retry
                    item["attempts"] += 1
                    item["priority"] += 1  # Lower priority on retry
                    self._queue.append(item)
                    
            except Exception as e:
                logger.exception(f"Queue processing error: {e}")
                
                if item["attempts"] < 3:
                    item["attempts"] += 1
                    self._queue.append(item)
            
            # Small delay between emails
            await asyncio.sleep(0.5)
        
        self._is_processing = False


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

email_service = EmailService()
email_queue = EmailQueue()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def send_email_background(
    to_email: str,
    email_type: EmailType,
    context: Dict[str, Any],
    language: str = "uz",
    to_name: Optional[str] = None,
) -> str:
    """Send email via background queue."""
    return await email_queue.enqueue(
        to_email=to_email,
        email_type=email_type,
        context=context,
        language=language,
        to_name=to_name,
    )









