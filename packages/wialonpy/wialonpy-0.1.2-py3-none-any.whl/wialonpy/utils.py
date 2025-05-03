import requests

DEFAULT_WIALON_URL = "https://hst-api.wialon.com/wialon/ajax.html"

def wialon_get_session_eid(w_token: str, wialon_url: str = DEFAULT_WIALON_URL) -> str | None:
    """
    Authenticate with Wialon API using a token and return the session ID (eid).

    Args:
        w_token (str): Wialon API token.
        wialon_url (str, optional): Full URL to the Wialon API endpoint.
            Defaults to "https://hst-api.wialon.com/wialon/ajax.html".

    Returns:
        str | None: Session ID (eid) if successful, otherwise None.

    Raises:
        requests.exceptions.RequestException: If the request fails due to network or HTTP issues.

    Example:
        eid = wialon_get_session_eid("your_token_here")
        eid = wialon_get_session_eid("your_token", "https://wialontest.com/wialon/ajax.html")
    """
    url = f'{wialon_url}?svc=token/login&params={{"token":"{w_token}"}}'
    response = requests.post(url)
    response.raise_for_status()
    return response.json().get("eid")