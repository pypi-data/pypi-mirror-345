from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session_with_retries():
    """
    Creates a requests Session with retry capabilities for improved resilience.

    Returns:
        Session: A requests Session configured with retry capabilities.
    """
    session = Session()
    retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=2,  # Exponential backoff factor
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
