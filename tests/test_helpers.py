import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

from hotmart_python import Hotmart

client_id = "b32450c1-1352-246a-b6d3-d49d6db815ea"
client_secret = "90bcc221-cebd-5a5b-00e2-72cab47d9282"
basic = (
    "Basic YjIzNTQxYzAtMyEzNS20MjVhLWI1ZDItZDM4ZDVkYjcwNGVhOjA5Y2JiMTEz"
    "LWRiZWMtNGI0YS05OWUxLTI3Y2FiNDdkOTI4Mg=="
)


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.hotmart = Hotmart(
            client_id=client_id, client_secret=client_secret, basic=basic
        )

    # Build Payload
    def test_build_payload_with_valid_arguments(self):
        """
        None values should be ignored
        """
        result = self.hotmart._build_payload(
            buyer_email="test@example.com",
            purchase_value=123,
            is_buyer=True,
            param4=None,
        )

        self.assertEqual(
            result,
            {
                "buyer_email": "test@example.com",
                "purchase_value": 123,
                "is_buyer": True,
            },
        )

    def test_build_payload_with_no_arguments(self):
        """
        No arguments should return an empty dictionary
        """
        result = self.hotmart._build_payload()
        self.assertEqual(result, {})

    # Handle Response
    def test_handle_response_single_dict_response(self):
        response = {"key": "value"}
        expected_result = [response]
        self.assertEqual(self.hotmart._handle_response(response), expected_result)

    def test_handle_response_list_of_dicts_response(self):
        response = [{"key1": "value1"}, {"key2": "value2"}]
        self.assertEqual(self.hotmart._handle_response(response), response)

    def test_handle_response_non_dict_non_list_response(self):
        response = "invalid_response"
        with self.assertRaises(ValueError):
            self.hotmart._handle_response(response)  # noqa

    # Build URL
    def test_build_url_with_valid_endpoint_payments(self):
        result = self.hotmart._build_url("payments")
        expected_result = "https://developers.hotmart.com/payments/api/v1"
        self.assertEqual(result, expected_result)

    def test_build_url_with_valid_endpoint_club(self):
        result = self.hotmart._build_url("club")
        expected_result = "https://developers.hotmart.com/club/api/v1"
        self.assertEqual(result, expected_result)

    def test_build_url_with_valid_endpoint_sandbox_payments(self):
        self.hotmart.sandbox = True
        result = self.hotmart._build_url("payments")
        expected_result = "https://sandbox.hotmart.com/payments/api/v1"
        self.assertEqual(result, expected_result)

    def test_build_url_with_valid_endpoint_sandbox_club(self):
        self.hotmart.sandbox = True
        result = self.hotmart._build_url("club")
        expected_result = "https://sandbox.hotmart.com/club/api/v1"
        self.assertEqual(result, expected_result)

    def test_build_url_with_invalid_endpoint(self):
        with self.assertRaises(ValueError):
            self.hotmart._build_url("invalid_endpoint")

    # Sandbox Mode
    def test_sandbox_mode_true(self):
        self.hotmart.sandbox = True
        self.assertTrue(self.hotmart.sandbox)

    def test_sandbox_mode_false(self):
        self.assertFalse(self.hotmart.sandbox)

    # Make Request
    @patch("requests.get")
    def test_make_request_successful(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"items":[{"some":"info"}]}'
        mock_response.json.return_value = {"items": [{"some": "info"}]}
        mock_get.return_value = mock_response
        result = self.hotmart._make_request(
            requests.get,
            "https://developers.hotmart.com/" "payments/api/v1/sales/history",
        )

        self.assertEqual(result, {"items": [{"some": "info"}]})

    def test_make_request_http_error_403(self):
        """
        Checks if the exception is raised and a log hint it's logged.
        :return:
        """
        method_mock = MagicMock()
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"
        headers = {"Authorization": basic, "Content-Type": "application/json"}
        params = {"buyer_email": "buyer@example.com"}
        body = {"subdomain": "my_subdomain"}
        method_mock.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=403)
        )

        with self.assertRaises(requests.exceptions.HTTPError) as e:
            with patch.object(self.hotmart, "logger") as mock_logger:
                self.hotmart._make_request(method_mock, url, headers, params, body)

        self.assertEqual(e.exception.response.status_code, 403)
        mock_logger.error.assert_called_with(
            "Perhaps the credentials are for Sandbox Mode?"
        )

    def test_make_request_http_error_422(self):
        """
        Checks if the exception is raised and a log hint it's logged.
        :return:
        """
        method_mock = MagicMock()
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"
        headers = {"Authorization": basic, "Content-Type": "application/json"}
        params = {"buyer_email": "buyer@example.com"}
        body = {"subdomain": "my_subdomain"}
        method_mock.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=422)
        )

        with self.assertRaises(requests.exceptions.HTTPError) as e:
            with patch.object(self.hotmart, "logger") as mock_logger:
                self.hotmart._make_request(method_mock, url, headers, params, body)

        self.assertEqual(e.exception.response.status_code, 422)
        mock_logger.error.assert_called_with(
            "This usually happens when the request is missing" " body parameters."
        )

    def test_make_request_http_error_500(self):
        """
        Checks if the exception is raised and a log hint it's logged.
        :return:
        """
        self.hotmart.sandbox = True
        method_mock = MagicMock()
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"
        headers = {"Authorization": basic, "Content-Type": "application/json"}
        params = {"buyer_email": "buyer@example.com"}
        body = {"subdomain": "my_subdomain"}
        method_mock.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500)
        )

        with self.assertRaises(requests.exceptions.HTTPError) as e:
            with patch.object(self.hotmart, "logger") as mock_logger:
                self.hotmart._make_request(method_mock, url, headers, params, body)

        self.assertEqual(e.exception.response.status_code, 500)
        mock_logger.error.assert_any_call(
            "This happens with some endpoints in the Sandbox Mode."
        )
        mock_logger.error.assert_any_call(
            "Usually the API it's not down, it's just a bug."
        )

    def test_make_request_http_general_error(self):
        """
        Checks if the exception is raised when errors are different from 401, 403, 422 or 500.
        :return:
        """
        method_mock = MagicMock()
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"
        headers = {"Authorization": basic, "Content-Type": "application/json"}
        params = {"buyer_email": "buyer@example.com"}
        body = {"subdomain": "my_subdomain"}
        method_mock.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=418)
        )

        with self.assertRaises(requests.exceptions.HTTPError) as e:
            self.hotmart._make_request(method_mock, url, headers, params, body)

        self.assertEqual(e.exception.response.status_code, 418)
        self.assertRaises(requests.exceptions.HTTPError)

    # Is token expired
    @patch("time.time")
    def test_is_token_expired_when_expiry_in_past(self, mock_time):
        mock_time.return_value = 100
        self.hotmart.token_expires_at = 99
        self.assertTrue(self.hotmart._is_token_expired())

    @patch("time.time")
    def test_is_token_expired_when_expiry_in_future(self, mock_time):
        mock_time.return_value = 100
        self.hotmart.token_expires_at = 101
        self.assertFalse(self.hotmart._is_token_expired())

    # Fetch new token
    @patch.object(Hotmart, "_make_request")
    def test_fetch_new_token_obtained_successfully(self, mock_make_request):
        mock_make_request.return_value = {"access_token": "test_token"}
        token = self.hotmart._fetch_new_token()
        self.assertEqual(token, "test_token")

    @patch("requests.post")
    def test_fetch_new_token_obtained_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException
        with self.assertRaises(requests.exceptions.RequestException):
            self.hotmart._fetch_new_token()

    # Get token
    @patch.object(Hotmart, "_is_token_expired")
    @patch.object(Hotmart, "_fetch_new_token")
    def test_get_token_found_in_cache(
        self, mock_fetch_new_token, mock_is_token_expired
    ):

        mock_is_token_expired.return_value = False
        self.hotmart.token_cache = "test_token"
        token = self.hotmart._get_token()

        self.assertEqual(token, "test_token")
        mock_fetch_new_token.assert_not_called()

    @patch.object(Hotmart, "_is_token_expired")
    @patch.object(Hotmart, "_fetch_new_token")
    def test_get_token_not_in_cache_and_fetched_success(
        self, mock_fetch_new_token, mock_is_token_expired
    ):

        mock_is_token_expired.return_value = True
        mock_fetch_new_token.return_value = "new_token"
        token = self.hotmart._get_token()
        self.assertEqual(token, "new_token")

    @patch.object(Hotmart, "_is_token_expired")
    @patch.object(Hotmart, "_fetch_new_token")
    def test_get_token_not_in_cache_and_fetch_failed(
        self, mock_fetch_new_token, mock_is_token_expired
    ):

        mock_is_token_expired.return_value = True
        mock_fetch_new_token.return_value = None
        token = self.hotmart._get_token()
        self.assertIsNone(token)

    # Request with token
    @patch.object(Hotmart, "_get_token")
    @patch.object(Hotmart, "_make_request")
    def test_request_with_token_successful(self, mock_make_request, mock_get_token):

        mock_get_token.return_value = "test_token"
        mock_make_request.return_value = {"success": True}
        result = self.hotmart._request_with_token("GET", "https://example.com")
        self.assertEqual(result, [{"success": True}])

    @patch.object(Hotmart, "_get_token")
    @patch.object(Hotmart, "_make_request")
    def test_request_with_token_failed(self, mock_make_request, mock_get_token):

        mock_get_token.return_value = "test_token"
        mock_make_request.side_effect = requests.exceptions.RequestException
        with self.assertRaises(requests.exceptions.RequestException):
            self.hotmart._request_with_token("GET", "https://example.com")

    @patch.object(Hotmart, "_get_token")
    def test_request_with_token_unsupported_method(self, mock_get_token):

        mock_get_token.return_value = "test_token"
        with self.assertRaises(ValueError):
            self.hotmart._request_with_token("PUT", "https://example.com")


if __name__ == "__main__":
    unittest.main()
