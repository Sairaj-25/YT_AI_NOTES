import unittest

from core.oauth import build_github_redirect_uri


class DummyRequest:
    def __init__(self, host: str):
        self._host = host

    def url_for(self, name: str):
        return f"http://{self._host}/api/v1/auth/github/callback"


class GitHubRedirectUriTests(unittest.TestCase):
    def test_prefers_the_configured_github_callback_url(self):
        request = DummyRequest("127.0.0.1:8000")
        redirect_uri = build_github_redirect_uri(
            request,
            "http://localhost:8000/api/v1/auth/github/callback",
        )
        self.assertEqual(
            redirect_uri, "http://localhost:8000/api/v1/auth/github/callback"
        )

    def test_strips_surrounding_quotes_from_the_configured_callback_url(self):
        request = DummyRequest("127.0.0.1:8000")
        redirect_uri = build_github_redirect_uri(
            request,
            '"http://localhost:8000/api/v1/auth/github/callback"',
        )
        self.assertEqual(
            redirect_uri, "http://localhost:8000/api/v1/auth/github/callback"
        )

    def test_falls_back_to_the_request_url_when_no_callback_is_configured(self):
        request = DummyRequest("localhost:8000")
        redirect_uri = build_github_redirect_uri(request, "")
        self.assertEqual(
            redirect_uri, "http://localhost:8000/api/v1/auth/github/callback"
        )


if __name__ == "__main__":
    unittest.main()
