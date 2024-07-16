import logging
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import coloredlogs
import requests

Response = List[Dict[str, Any]]

# Base Logging Configs
logger = logging.getLogger(__name__)

# Coloredlogs Configs
coloredFormatter = coloredlogs.ColoredFormatter(
    fmt="[%(name)s] %(asctime)s  %(message)s",
    level_styles=dict(
        debug=dict(color="white"),
        info=dict(color="blue"),
        warning=dict(color="yellow", bright=True),
        error=dict(color="red", bold=True, bright=True),
        critical=dict(color="black", bold=True, background="red"),
    ),
    field_styles=dict(
        name=dict(color="white"),
        asctime=dict(color="white"),
        funcName=dict(color="white"),
        lineno=dict(color="white"),
    ),
)

# Console Handler Configs
ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(fmt=coloredFormatter)
logger.addHandler(hdlr=ch)
logger.setLevel(level=logging.CRITICAL)


class Hotmart:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        basic: str,
        api_version: int = 1,
        sandbox: bool = False,
        log_level: int = logging.CRITICAL,
    ) -> None:
        """
        Initializes the Hotmart API client.

        Full docs can be found at https://developers.hotmart.com/docs/en/

        Args:
            client_id (str): The Client ID provided by Hotmart.
            client_secret (str): The Client Secret provided by Hotmart.
            basic (str): The Basic Token provided by Hotmart.
            api_version (int): The version of the API to use (default is "1").
            sandbox (bool): Whether to use the sandbox or not (default is False).
            log_level (int): The logging level to use (default is logging.INFO).

        Returns:
            None
        """

        self.id = client_id
        self.secret = client_secret
        self.basic = basic
        self.sandbox = sandbox
        self.api_version = api_version

        # Token caching and some logic to do better logging.
        self.token_cache = None
        self.token_expires_at = None
        self.token_found_in_cache = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    @staticmethod
    def _build_payload(**kwargs: Any) -> Dict[str, Any]:
        """
        Builds a payload with the given kwargs, ignoring the ones
        with None value

        Args:
            kwargs (Any): Expected kwargs can be found in the "Request parameters"
             section of the API Docs.

        Returns:
            Dict[str, Any]: The built payload as a dictionary.
        """
        payload = {}
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        return payload

    @staticmethod
    def _handle_response(
        response: Tuple[Dict[str, Any], List[Dict[str, Any]]], enhance=True
    ) -> Response:
        """
        Standardizes the output of the response to always be a list of dictionaries.

        Args:
            response (Response): The original response which can be
            a dictionary or a list of dictionaries.
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)

        Returns:
            A list of dictionaries.
        """
        try:
            if enhance:
                if isinstance(response, dict) and response["items"]:
                    return response["items"]

                if isinstance(response, dict) and response["lessons"]:
                    return response["lessons"]

                if isinstance(response, list):
                    return response

            if not enhance:
                if isinstance(response, dict):
                    return [response]

                if isinstance(response, list):
                    return response

            raise ValueError("Response must be a dictionary or a list of dictionaries.")
        except KeyError:
            return [response]

    def _build_url(self, endpoint_type: str) -> str:
        """
        Builds the URLs for better dynamic requests.
        Args:
            endpoint_type (str): Supported types: payments or club

        Returns:
            str: The full URL.
        """

        supported_types = ["payments", "club"]
        if endpoint_type.lower() not in supported_types:
            raise ValueError(f"Unsupported endpoint type: {endpoint_type}")

        return (
            f'https://{"sandbox" if self.sandbox else "developers"}.hotmart.com/'
            f"{endpoint_type.lower()}/api/v{self.api_version}"
        )

    def _sandbox_error_warning(self) -> None:
        """
        Log a warning message about the Hotmart Sandbox API not supporting some requests

        Returns:
            None
        """
        self.logger.warning(
            "At the date of last update for this library"
            " the Hotmart Sandbox API does NOT supported this method."
        )
        self.logger.warning("This method probably won't work in the Sandbox mode.")
        return

    def _log_instance_mode(self) -> None:
        """
        Logs the instance mode (Sandbox or Production).

        Returns:
            None
        """
        return self.logger.warning(
            f"Instance in {'Sandbox' if self.sandbox else 'Production'} mode"
        )

    def _make_request(
        self,
        method: Any,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, str]] = None,
        log_level: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Makes a request to the given url.

        Args:
            method (Any): The request method (e.g, requests.get, requests.post).
            url (str): The URL to make the request to.
            headers (Optional[Dict[str, str]]): Optional request headers.
            params (Optional[Dict[str, str]]): Optional request parameters.
            log_level (Optional[int]): The logging level for this method (default is
            None, inherits from class level).
        Returns:
             The JSON response if the request was successful, None otherwise.
        """

        if log_level is not None:
            logger = logging.getLogger(__name__)  # noqa
            logger.setLevel(log_level)

        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request headers: {headers}")
        self.logger.debug(f"Request params: {params}")
        self.logger.debug(f"Request body: {body}")

        try:
            response = method(url, headers=headers, params=params, data=body)
            self.logger.debug(f"Response content: {response.text}")
            if response.status_code == requests.codes.ok:
                return response.json()
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            # noinspection PyUnboundLocalVariable
            if e.response.status_code == 401 or e.response.status_code == 403:
                if self.sandbox:
                    self.logger.error(
                        "Perhaps the credentials aren't for Sandbox Mode?"
                    )
                else:
                    self.logger.error("Perhaps the credentials are for Sandbox Mode?")
                raise e

            if e.response.status_code == 422:
                self.logger.error(f"Error {e.response.status_code}")
                self.logger.error(
                    "This usually happens when the request is missing"
                    " body parameters."
                )
                raise e

            if e.response.status_code == 500 and self.sandbox:
                self.logger.error(
                    "This happens with some endpoints in the Sandbox Mode."
                )
                self.logger.error("Usually the API it's not down, it's just a bug.")

            raise e

    def _is_token_expired(self) -> bool:
        """
        Checks if the current token has expired.
        Returns:
             True if the token has expired, False otherwise.
        """
        return self.token_expires_at is not None and self.token_expires_at < time.time()

    def _fetch_new_token(self) -> str:
        """
        Requests a new token from the Hotmart API.
        Returns:
            str: A new access token.

        """
        self.logger.debug("Fetching a new access token.")

        method_url = "https://api-sec-vlc.hotmart.com/security/oauth/token"
        headers = {"Authorization": self.basic}
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.id,
            "client_secret": self.secret,
        }

        response = self._make_request(
            requests.post, method_url, headers=headers, params=payload
        )
        self.logger.debug("Token obtained successfully")
        return response["access_token"]

    def _get_token(self) -> str:
        """
        Retrieves an access token to authenticate requests.
        Returns:
             str: The access token if obtained successfully, otherwise None.
        """
        if not self._is_token_expired() and self.token_cache is not None:
            if not self.token_found_in_cache:
                self.logger.debug("Token found in cache.")
                self.token_found_in_cache = True
            return self.token_cache

        self.logger.debug("Token not found in cache or expired.")

        token = self._fetch_new_token()
        if token is not None:
            self.token_cache = token
            self.token_found_in_cache = False
        return token

    def _request_with_token(
        self,
        method: str,
        url: str,
        enhance: bool = None,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Makes an authenticated request (GET, POST, PATCH, etc.) to the
        specified URL with the given body or params.
        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', 'PATCH').
            url (str): the URL to make the request to.
            enhance (Optional[bool]): Whether to enhance the response or not.
            body (Optional[Dict[str, Any]]): Optional request body.
            params (Optional[Dict[str, Any]]): Optional request parameters.
        Returns:
             The JSON Response if successful, otherwise raises an exception.
        """
        token = self._get_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        method_mapping = {
            "GET": requests.get,
            "POST": requests.post,
            "PATCH": requests.patch,
            "DELETE": requests.delete,
        }

        if method.upper() not in method_mapping:
            raise ValueError(f"Unsupported method: {method}")

        response = self._make_request(
            method_mapping[method.upper()],
            url,
            headers=headers,
            params=params,
            body=body,
        )

        return self._handle_response(response, enhance=enhance)

    def get_sales_history(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves sales history data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
            Sales history data.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/sales/history"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_sales_summary(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves sales summary data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
             Sales summary data if available, otherwise None.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/sales/summary"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_sales_participants(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves sales user data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
             Sales user data if available, otherwise None.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/sales/users"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_sales_commissions(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves sales commissions data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
            Sales commissions data if available, otherwise None.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/sales/commissions"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_sales_price_details(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves sales price details based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
             Sales price details if available, otherwise None.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/sales/price/details"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_subscriptions(self, enhance: bool = True, **kwargs: Any) -> Response:
        """
        Retrieves subscription data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
            Subscription data if available, otherwise None.
        """

        self._log_instance_mode()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_subscriptions_summary(
        self, enhance: bool = True, **kwargs: Any
    ) -> Response:
        """
        Retrieves subscription summary data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only the
            items. (Default is True)
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
             Subscription data if available, otherwise None.
        """

        self._log_instance_mode()
        self._sandbox_error_warning()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions/summary"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def get_subscription_purchases(
        self, subscriber_code: str, enhance: bool = True, **kwargs: Any
    ) -> Response:
        """
        Retrieves subscription purchases data based on the provided filters.

        Args:
            enhance (bool): When True, discards page_info and returns only
             the items. (Default is True)
            subscriber_code (str): The subscriber code to filter the request.
            kwargs (Any): Filters to apply on the request. Expected kwargs can be found
            in the "Request parameters" section of the API Docs.

        Returns:
             Subscription purchases data if available, otherwise None.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions/{subscriber_code}/purchases"
        payload = self._build_payload(**kwargs)
        return self._request_with_token(
            method=method, url=url, params=payload, enhance=enhance
        )

    def cancel_subscription(
        self, subscriber_code: List[str], send_email: bool = True
    ) -> Response:
        """
        Cancels a subscription.

        Args:
            subscriber_code (List[str]): The subscriber code you want to cancel
            the subscription.
            send_email (bool): Whether to email the subscriber or not (default is True).
        :return:
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "post"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions/cancel"
        payload = {"subscriber_code": subscriber_code, "send_email": send_email}
        return self._request_with_token(method=method, url=url, body=payload)

    def reactivate_and_charge_subscription(
        self, subscriber_code: List[str], charge: bool = False
    ) -> Response:
        """
        Reactivates and charges a subscription.

        Args:
        subscriber_code (List[str]): The subscriber code you want to reactivate
        and charge the subscription
        charge (bool): Whether to make a new charge to the subscriber
        or not (default is False).
        Returns:
             A dict with the response.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "post"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions/reactivate"
        payload = {"subscriber_code": subscriber_code, "charge": charge}
        return self._request_with_token(method=method, url=url, body=payload)

    def change_due_day(self, subscriber_code: str, new_due_day: int) -> Response:
        """
        Changes the due day of a subscription.

        Args:
            subscriber_code (str): The subscriber code you want to change the due day.
            new_due_day (int): The new due day you want to set.

        Response:
            Empty body, just a status code 200 is successful.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "patch"
        base_url = self._build_url("payments")
        url = f"{base_url}/subscriptions/{subscriber_code}"
        payload = {"due_day": new_due_day}
        return self._request_with_token(method=method, url=url, body=payload)

    def create_coupon(
        self, product_id: str, coupon_code: str, discount: float
    ) -> Response:
        """
        Creates a coupon for a product.
        Args:
            product_id (str): UID of the product you want to create the coupon for.
            coupon_code (str): The code of the coupon you want to create.
            discount (float): The discount you want to apply to the coupon, must be
            greater than 0 and less than 0.99.
        Returns:
             Empty body, just a status code 200 is successful.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "post"
        base_url = self._build_url("payments")
        url = f"{base_url}/product/{product_id}/coupon"
        payload = {"code": coupon_code, "discount": discount}
        return self._request_with_token(method=method, url=url, body=payload)

    def get_coupon(self, product_id: str, code: str, enhance: bool = True) -> Response:
        """
        Retrieves a coupon for a product.

        Args:
        enhance (bool): When True, discards page_info and returns only the
        items. (Default is True).
        product_id (str): UID of the product you want to retrieve the coupon for.
        code (str): The code of the coupon you want to retrieve.

        Returns:
             All Coupons for the product.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "get"
        base_url = self._build_url("payments")
        url = f"{base_url}/coupon/product/{product_id}"
        params = {"code": code}
        return self._request_with_token(
            method=method, url=url, params=params, enhance=enhance
        )

    def delete_coupon(self, coupon_id):
        """
        Deletes a coupon.

        Args:
            coupon_id (str):
        
        Return:
             Empty body, just a status code 200 is successful.
        """

        self._log_instance_mode()
        if self.sandbox:
            self._sandbox_error_warning()

        method = "delete"
        base_url = self._build_url("payments")
        url = f"{base_url}/coupon/{coupon_id}"
        return self._request_with_token(method=method, url=url)
