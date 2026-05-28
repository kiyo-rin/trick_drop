import imaplib, email, os
import toml
secrets = toml.load("../.streamlit/secrets.toml")
user = secrets["email"]["gmail_kiyota_user"]
password = secrets["email"]["gmail_kiyota_pass"]

server = "imap.gmail.com"
mail = imaplib.IMAP4_SSL(server)
mail.login(user, password)
mail.select("inbox")

from datetime import datetime, timedelta
search_date = (datetime.now() - timedelta(days=10)).strftime("%d-%b-%Y")
status, response = mail.search(None, f'SINCE {search_date}')
email_ids = response[0].split()[-1000:]
ids_str = b",".join(email_ids[:100]) # test first 100

import time
start = time.time()
status, data = mail.fetch(ids_str, '(BODY.PEEK[HEADER] BODY.PEEK[TEXT])')
print("Fetched 100 emails in", time.time() - start, "seconds")
print("Number of parts:", len(data))
mail.logout()
