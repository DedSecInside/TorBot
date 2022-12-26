"""
This module is used to gather data for analysis using thehiddenwiki.org.
"""
import datetime
import uuid

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar
from threadsafe.safe_csv import SafeDictWriter

from .utils import join_local_path
from .validators import validate_link


def parse_links(html: str):
    """Parses HTML page to extract links.

    Returns:
        (list): List of all valid links found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a')
    return [tag['href'] for tag in tags if validate_link(tag['href'])]


def parse_meta_tags(soup: BeautifulSoup):
    """Retrieve all meta elements from HTML object.

    Returns:
        list: List containing content from meta tags
    """
    meta_tags = soup.find_all('meta')
    content_list = list()
    for tag in meta_tags:
        content_list.append(tag.attrs)
    return content_list


def get_links(url: str):
    resp = requests.get(url)
    links = parse_links(resp.text)
    return links


default_url = 'https://thehiddenwiki.org'


def collect_data(user_url: str):
    url = user_url if user_url is not None else default_url
    print(f"Gathering data for {url}")
    links = get_links(url)
    current_time = datetime.datetime.now().isoformat()
    file_name = f'torbot_{current_time}.csv'
    file_path = join_local_path(file_name)
    with open(file_path, 'w+') as outcsv:
        fieldnames = ['ID', 'Title', 'Metadata', 'Content']
        writer = SafeDictWriter(outcsv, fieldnames=fieldnames)
        bar = Bar('Processing...', max=len(links))
        for link in links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, 'html.parser')
            meta_tags = parse_meta_tags(soup)
            entry = {
                "ID": uuid.uuid4(),
                "Title": soup.title.string,
                "Metadata": meta_tags,
                "Content": soup.find('body')
            }
            writer.writerow(entry)
            bar.next()
    bar.finish()
    print(f'Data has been saved to {file_path}.')
