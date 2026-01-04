import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def enviar_email_smtp(destinatario, asunto, cuerpo_html):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    if not smtp_host or not smtp_user or not smtp_pass:
        raise Exception('Faltan variables SMTP en el entorno')

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, destinatario, msg.as_string())
