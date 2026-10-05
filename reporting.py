import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_email_report(sender_email, sender_password, recipient_email, subject, body, attachment_paths=None):
    msg = EmailMessage()
    msg['From'] = sender_email
    if isinstance(recipient_email, str):
        recipient_email = [recipient_email]
    msg['To'] = ', '.join(recipient_email)
    msg['Subject'] = subject
    msg.set_content(body)

    for path in attachment_paths or []:
        p = Path(path)
        if not p.exists():
            continue
        ctype, encoding = mimetypes.guess_type(str(p))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(p, 'rb') as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=p.name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
        print("Email enviado!")
