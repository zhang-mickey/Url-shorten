import re
import requests
import socket
from urllib.parse import urlparse


def is_valid_url(url):
    # special case: .. not allowed
    if re.search(r"\.\.", url):
        return False
    regex = r"^((http|https)://)[-a-zA-Z0-9@:%._+~#?&/=(),'–]{2,256}\.[a-z]{2,}([-a-zA-Z0-9@:%._+~#?&/=(),'–]*)$"
    r = re.compile(regex, re.IGNORECASE)
    return bool(r.fullmatch(url))

# URL_REGEX = re.compile(
#     r"^(https?://)?"
#     r"([a-zA-Z0-9.-]+)"  # domain/ ip address
#     r"(\.[a-zA-Z]{2,})"  # (.com, .org, .net, etc.)
#     r"(:\d{1,5})?"  # port
#     r"(/.*)?$"  # path
# )
#
# def is_valid_url(url):
#
#     return bool(URL_REGEX.match(url))


def domain_exists(url):
    """Check if the domain of a URL exists."""
    if not url.strip():
        return False
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

#Too slow

# def domain_exists(url):
#     try:
#         response = requests.get(url, timeout=5)
#         return response.status_code == 200
#     except requests.exceptions.RequestException:
#         return False  # In case of error (invalid URL, timeout, etc.)

