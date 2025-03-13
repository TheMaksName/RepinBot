import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from config import Settings

users_token = {}

def generate_verification_token():
    return secrets.token_urlsafe(8)


async def send_verification_mail(mail, token):
    body = f'Пожалуйста, подтвердите ваш email, введя этот код в Телеграм-боте: {token}'

    msg = MIMEMultipart()
    msg['From'] = Settings.USERNAME
    msg['To'] = mail
    msg['Subject'] = 'Подтверждение email'
    msg.attach(MIMEText(body, 'plain'))
    try:
        smtp_client = aiosmtplib.SMTP(hostname=Settings.SMTP_SERVER, port=Settings.SMTP_PORT, use_tls=True)
        await smtp_client.connect()
        await smtp_client.login(Settings.USERNAME, Settings.PASSWORD)
        await smtp_client.send_message(msg)
        print("Письмо отправлено")
    except Exception as e:
        print(e)
    finally:
        await smtp_client.quit()

async def start_verify_mail(mail, user_id):
    global users_token
    token  = generate_verification_token()
    users_token[user_id] = token
    await send_verification_mail(mail, token)
    print(users_token)

def check_verify_code(code, user_id):
    global users_token
    if users_token[user_id] == code:
        del users_token[user_id]
        return True
    else:
        return False
