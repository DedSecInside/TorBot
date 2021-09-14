import requests


class GoTor:
    @staticmethod
    def get_node(link, depth, address='localhost', port='8081'):
        url = f'http://{address}:{port}/tree?link={link}&depth={depth}'
        resp = requests.get(url)
        return resp.json()

    @staticmethod
    def get_ip(address='localhost', port='8081'):
        url = f'http://{address}:{port}/ip'
        resp = requests.get(url)
        return resp.text

    @staticmethod
    def get_emails(link, address='localhost', port='8081'):
        url = f'http://{address}:{port}/emails?link={link}'
        resp = requests.get(url)
        return resp.text
