"""
This module is used to gather data for analysis using thehiddenwiki.org.
"""
import datetime
import uuid
import os
import requests

from bs4 import BeautifulSoup
from progress.bar import Bar
from threadsafe.safe_csv import SafeDictWriter

from .config import get_data_directory
from .validators import validate_link
from .log import debug


def parse_links(html: str) -> list[str]:
    """
    Finds all anchor tags and parses the href attribute.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a')
    return [tag['href'] for tag in tags if validate_link(tag['href'])]


def parse_meta_tags(soup: BeautifulSoup) -> list[object]:
    """
    Parses all meta tags.
    """
    meta_tags = soup.find_all('meta')
    content_list = list()
    for tag in meta_tags:
        content_list.append(tag.attrs)
    return content_list


def get_links(url: str) -> list[str]:
    """
    Returns all valid links found on the URL.
    """
    resp = requests.get(url)
    links = parse_links(resp.text)
    return links


def collect_data(url: str = 'https://thehiddenwiki.org'):
    print(f"Gathering data for {url}")
    links = get_links(url)
    current_time = datetime.datetime.now().isoformat()
    file_name = f'torbot_{current_time}.csv'
    data_directory = get_data_directory()
    local_file_path = os.path.join(data_directory, file_name)
    with open(local_file_path, 'w+') as outcsv:
        fieldnames = ['ID', 'Title', 'Metadata', 'Content']
        writer = SafeDictWriter(outcsv, fieldnames=fieldnames)
        bar = Bar('Processing...', max=len(links))
        for link in links:
            try:
                resp = requests.get(link)
                soup = BeautifulSoup(resp.text, 'html.parser')
                meta_tags = parse_meta_tags(soup)
                entry = {
                    "ID": uuid.uuid4(),
                    "Title": soup.title.string if soup.title else "",
                    "Metadata": meta_tags,
                    "Content": soup.find('body')
                }
                writer.writerow(entry)
            except requests.exceptions.RequestException as e:
                print(f"Failed to connect to [{link}].")
                debug(e)
            bar.next()
    bar.finish()

    print(f'Data has been saved to {local_file_path}.')
