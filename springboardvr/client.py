import httpx

from .exceptions import InvalidCredentialsError
from .sessions import SessionAPI


class SpringboardVR(object):
    def __init__(self, account_email: str, account_password: str) -> None:
        self._client = httpx.Client()
        self._account_email = account_email
        self._perform_login(account_email, account_password)
        
        self.sessions = SessionAPI(self)

    def _perform_login(self, account_email: str, account_password: str) -> None:
        payload = {
            "query": """
                mutation ($email: String, $password: String) {
                    user: authenticateUser(email: $email, password: $password) {
                        token
                    }
                }
            """,
            "variables": {
                "email": account_email,
                "password": account_password,
            },
        }
        url = "https://api.springboardvr.com/graphql"
        res = self._client.post(url, json=payload)
        json = res.json()
        if "errors" in json:
            raise InvalidCredentialsError
        token = json["data"]["user"]["token"]
        self._client.headers["Authorization"] = f"Bearer {token}"
