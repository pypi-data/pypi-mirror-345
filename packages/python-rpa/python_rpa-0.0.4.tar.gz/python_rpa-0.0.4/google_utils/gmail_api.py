import os
import base64
import re
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API 권한 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def search_emails_with_attachments(service, query='to:me', max_results=1):
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def download_attachments(service, messages, save_dir='downloads'):
    os.makedirs(save_dir, exist_ok=True)
    downloaded_files = []

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        for part in message['payload'].get('parts', []):
            filename = part.get('filename')
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')

            if filename and attachment_id:
                print(f'📥 다운로드 중: {filename}')
                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=attachment_id
                ).execute()

                data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                path = os.path.join(save_dir, filename)
                with open(path, 'wb') as f:
                    f.write(data)

                downloaded_files.append(path)
                print(f'✅ 저장됨: {path}')
    
    return downloaded_files

