import imaplib, email, re
import toml
from email.header import decode_header

try:
    secrets = toml.load(".streamlit/secrets.toml")
    user = secrets["email"]["gmail_kiyota_user"]
    password = secrets["email"]["gmail_kiyota_pass"]

    server = "imap.gmail.com"
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, password)
    mail.select("inbox")

    status, response = mail.search(None, 'ALL')
    email_ids = response[0].split()[-100:]

    for e_id in reversed(email_ids):
        status, data = mail.fetch(e_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        subject_tuple = decode_header(msg['Subject'])[0]
        subject = subject_tuple[0]
        encoding = subject_tuple[1]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8', errors='ignore')
            
        from_addr = msg.get('From', '')
        if '注文確定' in subject and 'amazon.co.jp' in from_addr.lower() and 'YG' in subject:
            print("=== SUBJECT ===")
            print(subject)
            print("===============")
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode('utf-8', 'ignore')
                
            print("=== BODY FIRST 500 CHARS ===")
            print(body[:500])
            break
            
    mail.logout()
except Exception as e:
    print(e)
