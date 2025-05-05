# Authentication Guide

To interact with the Wialon API via `wialonpy`, you need to authenticate in two steps.

---

## Step 1: Obtain an API Token

You need a Wialon API token. You can:

- Generate it via the Wialon web interface.
- Or use login/password via Wialon's `core/login` method (not recommended for production).

---

## Step 2: Exchange Token for Session ID (`eid`)

Use the token to request a session ID using `wialon_get_session_eid`:

```python
from wialonpy.utils import wialon_get_session_eid

eid = wialon_get_session_eid("your_api_token")