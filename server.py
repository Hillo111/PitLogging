import asyncio
import websockets
from websockets.client import WebSocketClientProtocol
import json
import os
import subprocess
from math import ceil
import logging

LOG_FILES_DIR = '/Users/stas/Documents/ValorPit/logs/'
HOST_NAME = 'localhost'
HOST_PORT = 8765

BUFFER_SIZE = 4096
logging.getLogger().setLevel(logging.INFO)

async def send_file(sock: WebSocketClientProtocol, filepath: str):
    filename = os.path.split(filepath)[-1]
    filesize = os.path.getsize(filepath)
    chunk_count = ceil(filesize / BUFFER_SIZE)
    # print('sending file info')
    await sock.send(json.dumps({
        'filename': filename, 
        'chunk_count': chunk_count
    }))
    
    with open(filepath, 'rb') as f:
        for _ in range(chunk_count):
            data = f.read(BUFFER_SIZE)
            await sock.send(data)

async def send_files(sock: WebSocketClientProtocol, filepaths: list[str]):
    await sock.send(str(len(filepaths)))
    for path in filepaths:
        await send_file(sock, path)

def log_download_sequence(robo_ip='lvuser@10.68.0.2', robo_logs_dir='~/', local_logs_dir=''):
    if os.system("ping -c 1 " + robo_ip) != 0:
        return False
    
    subprocess.run(['scp', f'{robo_ip}:{os.path.join(robo_logs_dir, "*.wpilog")}', os.path.join(local_logs_dir, '.')])
    subprocess.run(['ssh', robo_ip])
    subprocess.run(['cd', robo_logs_dir])
    subprocess.run(['rm *.wpilog'])
    subprocess.run(['exit'])
    return True

async def serve(websocket: WebSocketClientProtocol):
    info = json.loads(await websocket.recv())
    if 'cmd' in info:
        if info['cmd'] == 'retrieve_logs':
            connected = log_download_sequence(local_logs_dir=LOG_FILES_DIR)
            if not connected:
                logging.warning('Unable to access robot')

            await websocket.send(json.dumps({
                'accessed': connected
            }))

            old_logs = info['saved_logs']
            logs = os.listdir(LOG_FILES_DIR)

            new_logs = []
            for log in logs:
                if log not in old_logs:
                    new_logs.append(os.path.join(LOG_FILES_DIR, log))

            logging.info(f'Sending {len(new_logs)} new logs')
            await send_files(websocket, new_logs)

async def main():
    async with websockets.serve(serve, HOST_NAME, HOST_PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())