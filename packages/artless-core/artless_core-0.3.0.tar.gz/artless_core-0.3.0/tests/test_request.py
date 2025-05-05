from io import BytesIO
from json import dumps
from typing import Any
from unittest import TestCase
from uuid import UUID

from artless import Request


def create_environ(data) -> dict[str, Any]:
    wsgi_input_data = data.get("wsgi.input", b"")
    content_length = len(wsgi_input_data)

    wsgi_input = BytesIO()
    wsgi_input.write(wsgi_input_data)
    wsgi_input.seek(0)

    environ = {
        "SCRIPT_URL": data.get("SCRIPT_URL", "/"),
        "PATH_INFO": data.get("PATH_INFO", "/some/test/url"),
        "CONTENT_LENGTH": content_length,
        "REQUEST_METHOD": data.get("REQUEST_METHOD", "GET"),
        "QUERY_STRING": data.get("QUERY_STRING", ""),
        "HTTP_HOST": data.get("HTTP_HOST", "test.com"),
        "HTTP_USER_AGENT": data.get("HTTP_USER_AGENT", "test ua"),
        "wsgi.input": wsgi_input,
    }

    environ |= {k: v for k, v in data.items() if k.startswith("HTTP_")}

    return environ


class TestRequest(TestCase):
    def test_attributes(self):
        body = b"some data"
        headers = {
            "Content-Length": len(body),
            "Content-Type": "text/html; charset=utf-8",
            "Host": "test.com",
            "User-Agent": "test ua",
        }
        request = Request(
            method="GET", url="/some/test/url?a=10&b=foo&b=bar#some-fragment", headers=headers, body=body
        )

        self.assertIsInstance(request.id, UUID)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.path, "/some/test/url")
        self.assertEqual(request.query, "a=10&b=foo&b=bar")
        self.assertEqual(request.fragment, "some-fragment")
        self.assertEqual(request.url, "/some/test/url?a=10&b=foo&b=bar#some-fragment")
        self.assertEqual(request.params, {"a": "10", "b": ["foo", "bar"]})
        self.assertEqual(request.headers, headers)
        self.assertEqual(request.user_agent, "test ua")
        self.assertEqual(request.body, b"some data")
        self.assertEqual(repr(request), "<Request: GET /some/test/url?a=10&b=foo&b=bar#some-fragment>")

    # def test_request_body_without_ctype(self):
    #     wsgi_input = b"some data"
    #     environ = create_environ(
    #         {
    #             "QUERY_STRING": "a=10&b=foo&b=bar#some-fragment",
    #             "wsgi.input": wsgi_input,
    #         }
    #     )

    #     request = Request(environ)
    #     # Expected the raw data in the request body.
    #     self.assertEqual(request.body, b"some data")

    # def test_request_with_json(self):
    #     environ = create_environ(
    #         {
    #             "HTTP_CONTENT_TYPE": "application/json",
    #             "wsgi.input": dumps({"some": {"data": True}}).encode(),
    #         }
    #     )

    #     request = Request(environ)

    #     self.assertEqual(request.headers["Content-Type"], "application/json")
    #     self.assertEqual(request.body, {"some": {"data": True}})

    # def test_request_with_www_form_urlencoded(self):
    #     environ = create_environ(
    #         {
    #             "HTTP_CONTENT_TYPE": "application/x-www-form-urlencoded",
    #             "wsgi.input": b"a=10&b=test",
    #         }
    #     )

    #     request = Request(environ)

    #     self.assertEqual(request.headers["Content-Type"], "application/x-www-form-urlencoded")
    #     self.assertEqual(request.body, {"a": "10", "b": "test"})
