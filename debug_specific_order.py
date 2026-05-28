import streamlit as st
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

def check_specific():
    user = st.secrets["email"]["gmail_kiyota_user"]
    password = st.secrets["email"]["gmail_kiyota_pass"]
    server = "imap.gmail.com"
    
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, password)
    mail.select("inbox")
    
    # search for this specific order number if possible, or fetch recently
    status, response = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = response[0].split()
        latest_ids = email_ids[-2000:]
        
        chunk_size = 100
        for i in range(len(latest_ids)-1, -1, -chunk_size):
            start_idx = max(0, i - chunk_size + 1)
            chunk_ids = latest_ids[start_idx : i + 1]
            chunk_ids = chunk_ids[::-1]
            ids_str = b",".join(chunk_ids)
            
            status, data = mail.fetch(ids_str, '(BODY.PEEK[])')
            if status != 'OK': continue
            
            for response_part in data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    msg = email.message_from_bytes(raw_email)
                    
                    subject_tuple = decode_header(msg['Subject'])[0]
                    subject = subject_tuple[0]
                    encoding = subject_tuple[1]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8', errors='ignore')
                    
                    if '503-9460447-9971059' in str(msg) or '503-9460447-9971059' in subject:
                        print(f"FOUND ORDER! Subject: {subject}")
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body_bytes = part.get_payload(decode=True)
                                    if body_bytes:
                                        body = body_bytes.decode(part.get_content_charset() or 'utf-8', errors='ignore')
                                    break
                        else:
                            body_bytes = msg.get_payload(decode=True)
                            if body_bytes:
                                body = body_bytes.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                        
                        print("=== BODY ===")
                        print(body[:1000])
                        print("============")
                        
                        sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', subject) or re.search(r'(YG[A-Za-z0-9\-]+)', body)
                        sku = sku_match.group(1) if sku_match else "None"
                        print(f"SKU: {sku}")
                        
                        qty_match1 = re.search(r'数量\s*[:：]\s*(\d+)', body)
                        qty_match2 = re.search(r'数量\s*[:：]\s*(\d+)', body.replace('\r', '').replace('\n', ' '))
                        print(f"Regex match original: {qty_match1.group(1) if qty_match1 else 'None'}")
                        print(f"Regex match modified: {qty_match2.group(1) if qty_match2 else 'None'}")
                        return

check_specific()
