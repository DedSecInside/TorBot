import asyncio
import websockets

async def handle_msg(websocket, path):
    while True:
        msg = await websocket.recv()
        import pdb; pdb.set_trace()

def startWSServer():
    start_server = websocket.server(handle_msg, 'localhost', '8080')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
