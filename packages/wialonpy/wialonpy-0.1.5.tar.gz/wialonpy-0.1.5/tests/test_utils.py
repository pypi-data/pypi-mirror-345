from unittest.mock import patch

import pytest
import requests

from wialonpy.utils import get_session_eid


@patch("requests.post")
def test_wialon_get_session_eid_default_url(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"eid": "default-url-session-id"}

    result = get_session_eid("FAKE_TOKEN")
    assert result == "default-url-session-id"
    mock_post.assert_called_once()
    assert "hst-api.wialon.com" in mock_post.call_args[0][0]


@patch("requests.post")
def test_wialon_get_session_eid_custom_url(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"eid": "custom-url-session-id"}

    result = get_session_eid("FAKE_TOKEN", "https://w.glonass24.com/wialon/ajax.html")
    assert result == "custom-url-session-id"
    mock_post.assert_called_once()
    assert "glonass24.com" in mock_post.call_args[0][0]


@patch("requests.post")
def test_wialon_get_session_eid_http_error(mock_post):
    mock_post.return_value.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")

    with pytest.raises(requests.HTTPError):
        get_session_eid("BAD_TOKEN")
