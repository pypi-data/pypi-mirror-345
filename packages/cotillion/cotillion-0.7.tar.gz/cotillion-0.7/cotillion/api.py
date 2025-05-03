import json
import logging
from datetime import datetime
from datetime import timedelta
import time

import pytz
from deceit.api_client import ApiClient


log = logging.getLogger(__name__)


class Api(ApiClient):
    def __init__(self, client_id, client_secret, *args,
                 access_token=None, refresh_token=None, default_timeout=10, **kwargs):
        super().__init__(
            *args, default_timeout=default_timeout,
            base_url='https://api.lightspeedapp.com/API/V3',
            **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.session.mount('https://', self.adapter)
        self.authorization_url = 'https://cloud.lightspeedapp.com/auth/oauth/authorize'
        self.token_url = 'https://cloud.lightspeedapp.com/auth/oauth/token'
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = None
        self.l_account_id = None

    def authorize(self, scopes=None):  # pragma: no cover
        """
        Authorize the client using the OAuth2 authorization code flow.
        This method will redirect the user to the authorization URL and
        exchange the authorization code for an access token.
        """
        # Redirect the user to the authorization URL

        if scopes and isinstance(scopes, list):
            scopes = ' '.join(scopes)
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scopes or 'employee:all',
        }
        response = self.session.get(
            self.authorization_url,
            params=params)
        print(response.headers)
        print(response.text)

    # no cover: start
    def get_tokens(self, authorization_code):  # pragma: no cover
        """
        Exchange the authorization code for an access token and refresh token.
        """
        dt = datetime.now(pytz.utc)
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
        }
        response = self.session.post(self.token_url, data=payload)
        creds = response.json()
        dt += timedelta(seconds=creds.get('expires_in', 1800))
        self.access_token = creds['access_token']
        self.refresh_token = creds['refresh_token']
        self.expiry = dt
        creds['expires_at'] = dt
        return creds

    def fetch_token(self):
        """
        Fetch a new access token using the refresh token.
        """
        dt = datetime.now(pytz.utc)
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
        }
        response = self.session.post(self.token_url, data=payload)
        creds = response.json()
        dt += timedelta(seconds=creds.get('expires_in', 1800))
        self.access_token = creds['access_token']
        self.refresh_token = creds['refresh_token']
        self.expiry = dt
        creds['expires_at'] = dt
        return creds

    def headers(self, *args, **kwargs):
        return {
            'accept': 'application/json',
            'authorization': f'Bearer {self.access_token}',
        }

    @classmethod
    def handle_rate_limit(cls, response):
        headers = response.headers
        try:
            bucket = headers['X-LS-API-Bucket-Level']
            drip_rate = headers['X-LS-API-Drip-Rate']
            pieces = [ int(x) for x in bucket.split('/') ]
            current, n_max = pieces
            delta = n_max - current
            if delta < 3:  # pragma: no cover
                log.info('sleeping for %s seconds', delta)
                time.sleep(delta * float(drip_rate))
        except (KeyError, ValueError):  # pragma: no cover
            pass

    @property
    def account_id(self):
        if not self.l_account_id:
            data = self.get('Account.json')
            self.l_account_id = data['Account']['accountID']
        return self.l_account_id

    def sale_page(self, limit=100, timestamp=None, completed=None,
                  complete_time=None,
                  load_relations=None, raw=False, **kwargs):
        """
        Get a page of sales from the Lightspeed API.
        """
        load_relations = load_relations or [
            'SaleLines',
            'SaleLines.Discount',
            'SaleLines.Item',
            'SaleLines.Note',
            'SaleNotes',
            'SalePayments',
            'SalePayments.PaymentType',
            'SalePayments.CCCharge',
            'Customer',
            'Customer.Contact',
            'Discount',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
            'sort': '-timeStamp',
        }
        if timestamp:
            params['timeStamp'] = timestamp
        if complete_time:
            params['completeTime'] = complete_time
        if completed:
            params['completed'] = '=,true' if completed else '=,false'
        for key in kwargs:  # pragma: no cover
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/Sale.json'
        return self.get(route, params=params, raw=raw)

    def sale_payment_page(self, limit=100, create_time=None,
                          load_relations=None, raw=False, **kwargs):
        """
        Get a page of sale payments from the lightspeed api.
        """
        load_relations = load_relations or [
            'CCCharge',
            'PaymentType',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
            'sort': '-salePaymentID',
        }
        if create_time:
            params['createTime'] = create_time
        for key in kwargs:  # pragma: no cover
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/SalePayment.json'
        return self.get(route, params=params, raw=raw)

    def customer_page(self, limit=250, timestamp=None,
                      load_relations=None, raw=False, **kwargs):
        """
        Get a page of customers from the Lightspeed API.
        """
        load_relations = load_relations or [
            'Contact',
            'CustomerType',
            'Note',
            'CreditAccount',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
            'sort': '-timeStamp',
        }
        if timestamp:
            params['timeStamp'] = timestamp
        for key in kwargs:  # pragma: no cover
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/Customer.json'
        return self.get(route, params=params, raw=raw)

    def credit_account_page(self, limit=250, timestamp=None,
                            load_relations=None, raw=False, **kwargs):
        """
        Get a page of credit accounts from the Lightspeed API.
        """
        load_relations = load_relations or [
            'Contact',
            'WithdrawalPayments',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
            'sort': '-timeStamp',
        }
        if timestamp:
            params['timeStamp'] = timestamp
        for key in kwargs:  # pragma: no cover
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/CreditAccount.json'
        return self.get(route, params=params, raw=raw)

    def item_page(self, limit=100, timestamp=None,
                  load_relations=None, raw=False, **kwargs):
        """
        Get a page of items from the Lightspeed API.
        """
        load_relations = load_relations or [
            'ItemAttributes',
            'ItemAttributes.ItemAttributeSet',
            'Manufacturer',
            'ItemShops',
            'ItemVendorNums',
            'ItemComponents',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
            'sort': '-timeStamp',
        }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        for key in kwargs:  # pragma: no cover
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/Item.json'
        return self.get(route, params=params, raw=raw)

    def count_items(self, raw=False, timestamp=None, **kwargs):
        """
        get the count of items expected
        """
        params = { 'count': '1' }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        route = f'Account/{self.account_id}/Item.json'
        return self.get(route, params=params, raw=raw)

    def count_sales(self, raw=False, timestamp=None, **kwargs):
        """
        get the count of sales expected
        """
        params = { 'count': '1' }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        route = f'Account/{self.account_id}/Sale.json'
        return self.get(route, params=params, raw=raw)

    def count_sale_payments(self, raw=False, timestamp=None, **kwargs):
        """
        get the count of sale payments
        """
        params = { 'count': '1' }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        route = f'Account/{self.account_id}/SalePayment.json'
        return self.get(route, params=params, raw=raw)

    def count_customers(self, raw=False, timestamp=None, **kwargs):
        """
        Count number of customers from the Lightspeed API.
        """
        params = { 'count': '1' }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        route = f'Account/{self.account_id}/Customer.json'
        return self.get(route, params=params, raw=raw)

    def count_credit_accounts(self, raw=False, timestamp=None, **kwargs):
        """
        Count number of customers from the Lightspeed API.
        """
        params = { 'count': '1' }
        if timestamp:  # pragma: no cover
            params['timeStamp'] = timestamp
        route = f'Account/{self.account_id}/CreditAccount.json'
        return self.get(route, params=params, raw=raw)

    def shop_page(self, limit=100, load_relations=None, raw=False, **kwargs):
        """
        Get a page of items from the Lightspeed API.
        """
        load_relations = load_relations or [
            'Registers',
            'CCGateway',
            'Contact',
        ]
        params = {
            'limit': limit,
            'load_relations': json.dumps(load_relations),
        }
        for key in kwargs:
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/Shop.json'
        return self.get(route, params=params, raw=raw)

    def employee_page(self, limit=100, raw=False, **kwargs):
        """
        Get a page of items from the Lightspeed API.
        """
        params = {
            'limit': limit,
        }
        for key in kwargs:
            if key not in params:
                params[key] = kwargs[key]
        route = f'Account/{self.account_id}/Employee.json'
        return self.get(route, params=params, raw=raw)
