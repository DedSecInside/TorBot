import asyncio
import tldextract
import websockets
from .link import LinkNode

async def handle_msg(websocket, path):
    msg = await websocket.recv()
    ext = tldextract.extract(msg)
    if ext.domain == 'onion' or ext.suffix == 'onion':
        node = LinkNode(msg)
    else:
        node = LinkNode(msg, tor=False)
    for i, child in enumerate(node.get_children()):
        await websocket.send(str(i) + child)

def startWSServer():
    print('Starting WSServer on address localhost:8080')
    start_server = websockets.serve(handle_msg, 'localhost', '8080')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
