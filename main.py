from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import Flask, jsonify
import base64
import email

@app.route('/gmail/last', methods=['GET'])
def get_last_email():
    try:
        creds = Credentials.from_authorized_user_file('token.json')  # token real OAuth
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return jsonify({'status': 'ok', 'message': 'Caixa de entrada vazia'})

        msg_id = messages[0]['id']
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        body = ''
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8').strip()
                    break
        else:
            data = msg['payload']['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8').strip()

        return jsonify({
            'from': sender,
            'subject': subject,
            'received': date,
            'summary': body[:500]  # retorna até 500 caracteres
        })

    except Exception as e:
        return jsonify({'status': 'erro', 'detalhe': str(e)}), 500
