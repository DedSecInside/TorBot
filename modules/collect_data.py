import asyncio
import aiohttp
from aiohttp_socks import SocksConnector
import requests

from bs4 import BeautifulSoup
from .link import LinkNode


def parse_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find('div', attrs={'class': 'entry'})
    tags = entries.find_all('a')
    return [tag['href'] for tag in tags if LinkNode.valid_link(tag['href'])]

async def fetch(session, url):
    async with session.get(url) as resp:
        body = await resp.text()
        return body

async def collect_data():
    resp = requests.get('https://thehiddenwiki.org')
    links = parse_links(resp.content)
    conn = SocksConnector.from_url('socks5://127.0.0.1:9050')
    async with aiohttp.ClientSession(connector=conn) as session:
        for link in links:
            body = await fetch(session, link)
            print(body)
