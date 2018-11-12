import requests

proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
}
session = requests.session()
session.proxies = proxies
def proxyGET(url):
    return session.get(url)

