"""
This module is used to gather data for analysis using thehiddenwiki.org.
"""
import datetime
import uuid
import requests
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .link import LinkNode
from .utils import multi_thread
from .utils import find_file
from threadsafe.safe_csv import SafeDictWriter


dev_file = find_file("torbot_dev.env", "../")
if not dev_file:
    raise FileNotFoundError
load_dotenv(dotenv_path=dev_file)


def parse_links(html):
    """Parses HTML page to extract links.

    Args:
        html (str): HTML block code to be parsed.

    Returns:
        (list): List of all valid links found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find('div', attrs={'class': 'entry'})
    tags = entries.find_all('a')
    return [tag['href'] for tag in tags if LinkNode.valid_link(tag['href'])]


def parse_meta_tags(html_soup):
    """Retrieve all meta elements from HTML object.

    Args:
        html_soup (object): Parsed HTML object.

    Returns:
        list: List of the content from all meta elements.
    """
    meta_tags = html_soup.find_all('meta')
    meta_content = list()
    for meta in meta_tags:
        content = meta.attrs['content']
        meta_content.append(content)
    return meta_content


def collect_data():
    """Collect all relevant data from https://thehiddenwiki.org
    and save to file.
    """

    resp = requests.get('https://thehiddenwiki.org')
    links = parse_links(resp.content)
    time_stamp = datetime.datetime.now().isoformat()
    data_path = os.getenv('TORBOT_DATA_DIR')
    file_path = f'{data_path}/torbot_{time_stamp}.csv'
    with open(file_path, 'w+', newline='') as outcsv:
        writer = SafeDictWriter(outcsv, fieldnames=['ID',
                                                    'Title',
                                                    'Meta Tags',
                                                    'Content'])

    def handle_link(link):
        """ Collects meta data for single link, and prints to file.

        Args:
            link (str): Link to collect data from.
        """
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser',from_encoding="iso-8859-1")
        print(soup)
        body = soup.find('body')
        title = soup.title.getText() if soup.title else 'No Title'
        meta_tags = soup.find_all('meta')
        metadata = parse_meta_tags(soup)
        if len(metadata) < 1:
            metadata = [body]
        entry = {
            "ID": uuid.uuid4(),
            "Title": title.strip(),
            "Meta Tags": meta_tags,
            "Content": metadata
        }
        print(entry)
        writer.writerow(entry)
        
    multi_thread(links, handle_link)
