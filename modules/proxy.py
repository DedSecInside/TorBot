import requests

proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
}
session = requests.session()
session.proxies = proxies
def proxyGET(url, headers=None):
    if headers:
        return session.get(url, headers=headers)
    else:
        return session.get(url)

