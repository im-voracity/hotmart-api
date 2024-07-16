import unittest
from unittest.mock import Mock

from hotmart_python.decorators import paginate

client_id = 'b32450c1-1352-246a-b6d3-d49d6db815ea'
client_secret = '90bcc221-cebd-5a5b-00e2-72cab47d9282'
basic = ('Basic YjIzNTQxYzAtMyEzNS20MjVhLWI1ZDItZDM4ZDVkYjcwNGVhOjA5Y2JiMTEz'
         'LWRiZWMtNGI0YS05OWUxLTI3Y2FiNDdkOTI4Mg==')


class TestPaginateDecorator(unittest.TestCase):
    def setUp(self):
        self.func = Mock(return_value=[{
            "items": [{"id": 1}, {"id": 2}],
            "page_info": {
                "next_page_token": "token"
            }
        }])
        self.paginated_func = paginate(self.func)

    def test_paginate_when_no_next_page_token(self):
        self.func.return_value = [{'items': [{'id': 1}, {'id': 2}]}]
        result = self.paginated_func()
        self.assertEqual(result, [{'id': 1}, {'id': 2}])
        self.func.assert_called_once()

    def test_paginate_handles_empty_items(self):
        self.func.return_value = [{'items': []}]
        result = self.paginated_func()
        self.assertEqual(result, [])
        self.func.assert_called_once()

    def test_paginate_handles_no_items_key_in_response(self):
        self.func.return_value = [{}]
        result = self.paginated_func()
        self.assertEqual(result, [{}])
        self.func.assert_called_once()

    def test_paginate_response_is_list(self):
        self.func.return_value = [
            {"name": "Dripping 100 days", "page_order": 1},
            {"name": "Dripping BY_DATE", "page_order": 2},
            {"name": "Offer product", "page_order": 3}
        ]
        result = self.paginated_func()
        self.assertEqual(result, [
            {"name": "Dripping 100 days", "page_order": 1},
            {"name": "Dripping BY_DATE", "page_order": 2},
            {"name": "Offer product", "page_order": 3}
        ])
        self.func.assert_called_once()
