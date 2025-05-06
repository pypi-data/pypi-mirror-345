import requests, urllib3, socket, ssl

CONNECTION_ERRORS = (requests.exceptions.RequestException,
                requests.exceptions.ConnectionError,
                urllib3.exceptions.HTTPError,
                socket.error, ssl.SSLError, TimeoutError)