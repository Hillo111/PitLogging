import unittest
import asyncio
import os
import threading
from server import main
from client import retrieve_logs
import shutil
from time import sleep

class TestLogFileSend(unittest.TestCase):
    def test_log_file_send(self):
        for f in os.listdir('received_logs'):
            os.remove(f'received_logs/{f}')

        threading.Thread(target=asyncio.run, args=(main(),), daemon=False).start()
        sleep(1)
        asyncio.run(retrieve_logs())
        self.assertListEqual(os.listdir('logs'), os.listdir('received_logs'))

if __name__ == '__main__':
    unittest.main()