"""
This module is used to gather data for analysis using thehiddenwiki.org.
"""
import datetime
import uuid
import requests
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .utils import find_file
from threadsafe.safe_csv import SafeDictWriter
from progress.bar import Bar

from .validators import validate_link


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
    tags = soup.find_all('a')
    return [tag['href'] for tag in tags if validate_link(tag['href'])]


def parse_meta_tags(soup):
    """Retrieve all meta elements from HTML object.

    Args:
        soup (BeautifulSoup)

    Returns:
        list: List containing content from meta tags
    """
    meta_tags = soup.find_all('meta')
    content_list = list()
    for tag in meta_tags:
        content_list.append(tag.attrs)
    return content_list


def get_links(url):
    resp = requests.get(url)
    links = parse_links(resp.text)
    return links


default_url = 'https://thehiddenwiki.org'


def collect_data(user_url):
    url = user_url if user_url is not None else default_url
    print(f"Gathering data for {url}")
    links = get_links(url)
    # Create data directory if it doesn't exist
    data_directory = os.getenv('TORBOT_DATA_DIR')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    current_time = datetime.datetime.now().isoformat()
    file_name = f'torbot_{current_time}.csv'
    file_path = os.path.join(data_directory, file_name)
    with open(file_path, 'w+', newline='') as outcsv:
        fieldnames = ['ID', 'Title', 'Metadata', 'Content']
        writer = SafeDictWriter(outcsv, fieldnames=fieldnames)
        bar = Bar(f'Processing...', max=len(links))
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
