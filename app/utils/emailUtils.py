# app/utils/email_utils.py
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def send_unlock_email(user_info: dict, unlock_link: str):
    msg = EmailMessage()
    msg['Subject'] = f"Alerta: Usuario bloqueado - {user_info['email']}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = ADMIN_EMAIL
    
    bodyMessage = f"""
    Hola Administrador,
    
    La cuenta del usuario {user_info['email']} ha sido bloqueada debido a demasiados intentos de inicio de sesión fallidos.
    
    Nombre del usuario: {user_info['name']}
    ID de usuario: {user_info['id']}
    
    Puedes desbloquear la cuenta haciendo clic en el siguiente enlace:
    {unlock_link}
    
    Saludos,
    Tu equipo de seguridad <3
    """
    msg.set_content(bodyMessage)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email de notificación enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el email: {e}")