import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def enviar_email_gmail(destinatario, asunto, cuerpo_html):
    remitente = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASS')
    if not remitente or not password:
        raise Exception('No se encontró GMAIL_USER o GMAIL_PASS en el entorno')

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo_html, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
