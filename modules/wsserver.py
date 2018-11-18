"""
Module contains WebSocket server
"""

# Built-in Imports
import asyncio
import json
import logging

# Third Party Imports
import tldextract
import websockets
import requests
from bs4 import BeautifulSoup

# Local Imports
from .link import LinkNode
from .proxy import proxy_get, proxy_head


# Setting up logging format
# Logs include {time} {loglevel} {logmessage}
logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

async def handle_msg(websocket, path):
    """
    Handles incoming WebSocket messages from front-end.
    The appropriate action is taken based on the message.

    Args:
        websocket (websockets.protocol): websocket connection being used
        path (string): contains origin of websocket message
    """
    msg = await websocket.recv()
    data = json.loads(msg) # Load JSON response from front-end
    url = data['url']
    # action determines what we will do with the url
    action = data['action']
    if action == 'get_links':
        async for link in get_links(websocket, url):
            response = json.dumps(link)
            await websocket.send(response)

async def get_links(websocket, url):
    """
    Get links from url

    Args:
        url (string): url to get links from
    Returns:
        links (list): list containing links
    """
    ext = tldextract.extract(url)
    tor = ext.domain == 'onion' or ext.suffix == 'onion'

    # If there's an error with the url then we return it to be logged and sent
    try:
        if tor:
            response = proxy_get(url)
        else:
            response = requests.get(url)
    except Exception as err: 
        yield {'name': url, 'status': False, 'error': str(err)}
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    anchor_tags = soup.find_all('a')
    links = list()
    for anchor in anchor_tags:
        link = anchor.get('href')
        if link and LinkNode.valid_link(link):

            try:
                # Returns true if status_code is less than 400, false if not
                if tor:
                    status = proxy_head(link, timeout=5).ok
                else:
                    status = requests.head(link, timeout=5).ok
                yield {'name': link, 'status': status}
            except Exception as err:
                yield {'name': link, 'status': False, 'error': str(err)} 

def start_wsserver():
    """
    Starts WebSocketServer
    """
    print('Starting WSServer on address localhost:8080')
    start_server = websockets.serve(handle_msg, 'localhost', '8080')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
