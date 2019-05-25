"""
This module is used to gather data for analysis using thehiddenwiki.org.
"""
import csv
import uuid
import requests

from bs4 import BeautifulSoup
from .link import LinkNode
from .utils import multi_thread
from threading import Lock


def parse_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find('div', attrs={'class': 'entry'})
    tags = entries.find_all('a')
    return [tag['href'] for tag in tags if LinkNode.valid_link(tag['href'])]


def collect_data():
    resp = requests.get('https://thehiddenwiki.org')
    links = parse_links(resp.content)
    with open('tor_data.csv', 'w', newline='') as outcsv:
        writer = csv.DictWriter(outcsv,
                                fieldnames=['ID',
                                            'Title',
                                            'Meta Tags',
                                            'Content'])
        writer.writeheader()

        mutex = Lock()
        def handle_link(link):
            response = requests.get(link)
            body = response.content
            soup = BeautifulSoup(body, 'html.parser')
            title = soup.title.getText() if soup.title else 'No Title'
            meta_tags = soup.find_all('meta')
            entry = {
                "ID": uuid.uuid4(),
                "Title": title.strip(),
                "Meta Tags": meta_tags,
                "Content": body
            }
            print(entry)
            mutex.acquire()
            writer.writerow(entry)
            mutex.release()

        multi_thread(links, handle_link)
