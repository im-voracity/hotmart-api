import unittest
from unittest.mock import patch

from requests import Response

from hotmart_python import Hotmart

client_id = 'b32450c1-1352-246a-b6d3-d49d6db815ea'
client_secret = '90bcc221-cebd-5a5b-00e2-72cab47d9282'
basic = ('Basic YjIzNTQxYzAtMyEzNS20MjVhLWI1ZDItZDM4ZDVkYjcwNGVhOjA5Y2JiMTEz'
         'LWRiZWMtNGI0YS05OWUxLTI3Y2FiNDdkOTI4Mg==')


class TestSales(unittest.TestCase):
    def setUp(self):
        self.hotmart = Hotmart(client_id=client_id,
                               client_secret=client_secret,
                               basic=basic)

    @patch.object(Hotmart, '_request_with_token')
    def test_get_sales_history(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_sales_history(buyer_name='Paula', payment_type='BILLET')
        expected_url = 'https://developers.hotmart.com/payments/api/v1/sales/history'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'buyer_name': 'Paula',
                                                        'payment_type': 'BILLET'
                                                    },
                                                    enhance=True)

    @patch.object(Hotmart, '_request_with_token')
    def test_get_sales_summary(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_sales_summary(buyer_name='Paula', payment_type='BILLET')
        expected_url = 'https://developers.hotmart.com/payments/api/v1/sales/summary'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'buyer_name': 'Paula',
                                                        'payment_type': 'BILLET'
                                                    },
                                                    enhance=True)

    @patch.object(Hotmart, '_request_with_token')
    def test_get_sales_participants(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_sales_participants(buyer_name='Paula', transaction_status='APPROVED')
        expected_url = 'https://developers.hotmart.com/payments/api/v1/sales/users'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'buyer_name': 'Paula',
                                                        'transaction_status': 'APPROVED'
                                                    },
                                                    enhance=True)

    @patch.object(Hotmart, '_request_with_token')
    def test_get_sales_commissions(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_sales_commissions(commission_as='PRODUCER', transaction_status='APPROVED')
        expected_url = 'https://developers.hotmart.com/payments/api/v1/sales/commissions'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'commission_as': 'PRODUCER',
                                                        'transaction_status': 'APPROVED'
                                                    },
                                                    enhance=True)

    @patch.object(Hotmart, '_request_with_token')
    def test_get_sales_price_details(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_sales_price_details(payment_type='CREDIT_CARD',
                                             transaction_status='APPROVED')
        expected_url = 'https://developers.hotmart.com/payments/api/v1/sales/price/details'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'payment_type': 'CREDIT_CARD',
                                                        'transaction_status': 'APPROVED'
                                                    },
                                                    enhance=True)
