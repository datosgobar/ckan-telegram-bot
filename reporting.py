import smtplib
from email.message import EmailMessage

def send_email_report(sender_email, sender_password, recipient_email, subject, body, attachment_paths=None):
    msg = EmailMessage()
    msg['From'] = sender_email
    if isinstance(recipient_email, str):
        recipient_email = [recipient_email]
    msg['To'] = ', '.join(recipient_email)
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
        print("Email enviado!")