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
    def test_create_coupon(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_req_with_token.return_value = mock_response

        product_id = 'HP20219'
        coupon_code = 'testcoupon'
        coupon_discount = 0.5
        self.hotmart.create_coupon(product_id, coupon_code, coupon_discount)
        expected_url = f'https://developers.hotmart.com/payments/api/v1/product/{product_id}/coupon'

        mock_req_with_token.assert_called_once_with(method="post",
                                                    url=expected_url,
                                                    body={
                                                        'code': coupon_code,
                                                        'discount': coupon_discount
                                                    })

    @patch.object(Hotmart, '_request_with_token')
    def test_get_coupon(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        product_id = 'HP20219'
        coupon_code = 'testcoupon'
        self.hotmart.get_coupon(product_id, coupon_code)
        expected_url = f'https://developers.hotmart.com/payments/api/v1/coupon/product/{product_id}'

        mock_req_with_token.assert_called_once_with(method="get",
                                                    url=expected_url,
                                                    params={
                                                        'code': coupon_code
                                                    }, enhance=True)

    @patch.object(Hotmart, '_request_with_token')
    def test_delete_coupon(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {
            'items': [{
                'some': 'info'
            }]
        }
        mock_req_with_token.return_value = mock_response

        coupon_id = '123456'
        self.hotmart.delete_coupon(coupon_id)
        expected_url = f'https://developers.hotmart.com/payments/api/v1/coupon/{coupon_id}'

        mock_req_with_token.assert_called_once_with(method="delete", url=expected_url)
