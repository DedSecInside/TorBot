"""
Module contains WebSocket server
"""
import asyncio
import json
import tldextract
import websockets
import requests

from bs4 import BeautifulSoup
from .link import LinkNode
from .proxy import proxyGET


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
        links = get_links(url)
        # If get_links returns an exception then send an error as a response
        if isinstance(links, Exception):
            error = json.dumps({'error': str(links)})
            await websocket.send(error)
        else:
            for link in links:
                response = json.dumps({'link': link})
                await websocket.send(response)

def get_links(url):
    """
    Get links from url

    Args:
        url (string): url to get links from
    Returns:
        links (list): list containing links
    """
    ext = tldextract.extract(url)
    use_tor = ext.domain == 'onion' or ext.suffix == 'onion'
    try:
        if use_tor:
            response = proxyGET(url)
        else:
            response = requests.get(url)
    except Exception as err: 
        return err
    soup = BeautifulSoup(response.text, 'html.parser')
    anchor_tags = soup.find_all('a')
    links = list()
    for anchor in anchor_tags:
        link = anchor.get('href')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links

def start_wsserver():
    """
    Starts WebSocketServer
    """
    print('Starting WSServer on address localhost:8080')
    start_server = websockets.serve(handle_msg, 'localhost', '8080')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
