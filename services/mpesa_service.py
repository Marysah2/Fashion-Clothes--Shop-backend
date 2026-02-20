import requests
import base64
from datetime import datetime
import os

class MpesaService:
    def __init__(self):
        self.consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')
        self.business_shortcode = os.environ.get('MPESA_SHORTCODE')
        self.passkey = os.environ.get('MPESA_PASSKEY')
        self.callback_url = os.environ.get('MPESA_CALLBACK_URL')
        self.base_url = 'https://sandbox.safaricom.co.ke' if os.environ.get('MPESA_ENV') == 'sandbox' else 'https://api.safaricom.co.ke'

    def get_access_token(self):
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        auth = base64.b64encode(f'{self.consumer_key}:{self.consumer_secret}'.encode()).decode()
        headers = {'Authorization': f'Basic {auth}'}
        response = requests.get(url, headers=headers)
        return response.json().get('access_token')

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f'{self.business_shortcode}{self.passkey}{timestamp}'.encode()).decode()
        
        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        payload = {
            'BusinessShortCode': self.business_shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.business_shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
