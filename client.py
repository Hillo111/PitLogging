import asyncio
import websockets
from websockets.client import WebSocketClientProtocol
import json
import os
import logging

LOG_FILES_DIR = '/Users/stas/Documents/ValorPit/received_logs/'
URI = "ws://localhost:8765"

BUFFER_SIZE = 4096
logging.getLogger().setLevel(logging.INFO)

async def receive_file(sock: WebSocketClientProtocol, save_dir: str):
    info = json.loads(await sock.recv())
    # print('received file info:', info)

    fn = info['filename']
    chunk_count = info['chunk_count']
    fp = os.path.join(save_dir, fn)

    with open(fp, 'wb') as f:
        for _ in range(chunk_count):
            read_bytes = await sock.recv()
            f.write(read_bytes)

async def receive_files(sock: WebSocketClientProtocol, save_dir: str):
    file_count = int(await sock.recv())
    logging.info(f'Receiving {file_count} new files')
    for _ in range(file_count):
        await receive_file(sock, save_dir)

async def retrieve_logs():
    async with websockets.connect(URI) as websocket:
        # await send_file(websocket, 'FRC_20231007_210354.wpilog')
        await websocket.send(json.dumps({
            'cmd': 'retrieve_logs',
            'saved_logs': os.listdir(LOG_FILES_DIR)
        }))
        info = json.loads(await websocket.recv())
        if not info['accessed']:
            logging.warning('Server was unable to connect to robot')
        await receive_files(websocket, LOG_FILES_DIR)

if __name__ == "__main__":
    asyncio.run(retrieve_logs())
    