import asyncio
import websockets

async def handle_msg(websocket, path):
    msg = await websocket.recv()
    print(path)
    print(msg)

def startWSServer():
    start_server = websockets.serve(handle_msg, 'localhost', '8080')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
