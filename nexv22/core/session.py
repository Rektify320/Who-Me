import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session(retries=2):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s