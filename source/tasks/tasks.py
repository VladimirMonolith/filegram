import smtplib
from email.message import EmailMessage

from celery import Celery

from infra.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

celery = Celery('tasks', broker='redis://localhost:6379')


def get_email_template_uploads_report(username: str):
    """Рендерит email с отчётом о загрузках пользователя."""
    email = EmailMessage()
    email['Subject'] = 'Отчёт о загрузках'
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}! '
        f'Вот Ваш отчет о загрузках.</h1>'
        '<img src="https://asomobile.net/wp-content/uploads/2022/02/1-8.png">'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_email_uploads_report(username: str):
    """Отправляет email с отчётом о загрузках пользователя."""
    email = get_email_template_uploads_report(username=username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
 