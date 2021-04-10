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
from .link import LinkNode


dev_file = find_file("torbot_dev.env", "../")
if not dev_file:
    raise FileNotFoundError
load_dotenv(dotenv_path=dev_file)

default_url = 'https://thehiddenwiki.org'

def collect_data(url = default_url):
    print(f"Gathering data for {url}")

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

        node = LinkNode(url)
        node.load_data()
        children = node.get_children()
        bar = Bar(f'Processing...', max=len(children))
        for child in children:
            child.load_data()
            entry = {
                    "ID": uuid.uuid4(),
                    "Title": child.get_name(),
                    "Metadata": child.get_meta_tags(),
                    "Content": child.get_body()
            }
            writer.writerow(entry)
            bar.next()
    bar.finish()
    print(f'Data has been saved to {file_path}.')
