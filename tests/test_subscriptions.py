import unittest
from unittest.mock import patch

from requests import Response

from hotmart_python import Hotmart

client_id = "b32450c1-1352-246a-b6d3-d49d6db815ea"
client_secret = "90bcc221-cebd-5a5b-00e2-72cab47d9282"
basic = (
    "Basic YjIzNTQxYzAtMyEzNS20MjVhLWI1ZDItZDM4ZDVkYjcwNGVhOjA5Y2JiMTEz"
    "LWRiZWMtNGI0YS05OWUxLTI3Y2FiNDdkOTI4Mg=="
)


class TestSubscriptions(unittest.TestCase):
    def setUp(self):
        self.hotmart = Hotmart(
            client_id=client_id, client_secret=client_secret, basic=basic
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_get_subscriptions_success(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_subscriptions(param1="value1", param2="value2")
        expected_url = "https://developers.hotmart.com/payments/api/v1/subscriptions"

        mock_req_with_token.assert_called_once_with(
            method="get",
            url=expected_url,
            params={"param1": "value1", "param2": "value2"},
            enhance=True,
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_get_subscriptions_summary_success(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        self.hotmart.get_subscriptions_summary(param1="value1", param2="value2")
        expected_url = (
            "https://developers.hotmart.com/payments/api/v1/subscriptions/summary"
        )

        mock_req_with_token.assert_called_once_with(
            method="get",
            url=expected_url,
            params={"param1": "value1", "param2": "value2"},
            enhance=True,
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_get_subscriptions_purchases_success(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        subscriber_code = "HTMT20219"

        self.hotmart.get_subscription_purchases(
            subscriber_code=subscriber_code, param1="value1", param2="value2"
        )
        expected_url = (
            f"https://developers.hotmart.com/payments/api/v1"
            f"/subscriptions/{subscriber_code}/purchases"
        )

        mock_req_with_token.assert_called_once_with(
            method="get",
            url=expected_url,
            params={"param1": "value1", "param2": "value2"},
            enhance=True,
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_cancel_subscriptions(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        subscriber_code = ["HTMT20219"]
        expected_url = (
            "https://developers.hotmart.com/payments/api/v1" "/subscriptions/cancel"
        )
        expected_body = {"subscriber_code": subscriber_code, "send_email": True}

        self.hotmart.cancel_subscription(subscriber_code=subscriber_code)

        mock_req_with_token.assert_called_once_with(
            method="post", url=expected_url, body=expected_body
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_reactivate_and_charge_subscription(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        subscriber_code = ["HTMT20219"]
        expected_url = (
            "https://developers.hotmart.com/payments/api/v1" "/subscriptions/reactivate"
        )
        expected_body = {"subscriber_code": subscriber_code, "charge": False}

        self.hotmart.reactivate_and_charge_subscription(subscriber_code=subscriber_code)

        mock_req_with_token.assert_called_once_with(
            method="post", url=expected_url, body=expected_body
        )

    @patch.object(Hotmart, "_request_with_token")
    def test_change_due_day(self, mock_req_with_token):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.return_value = {"items": [{"some": "info"}]}
        mock_req_with_token.return_value = mock_response

        subscriber_code = "HTMT20219"
        expected_url = (
            f"https://developers.hotmart.com/payments/api/v1"
            f"/subscriptions/{subscriber_code}"
        )
        expected_body = {"due_day": 25}

        self.hotmart.change_due_day(subscriber_code, 25)

        mock_req_with_token.assert_called_once_with(
            method="patch", url=expected_url, body=expected_body
        )
