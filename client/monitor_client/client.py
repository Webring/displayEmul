import datetime
import socket
import struct
from typing import Tuple

import cv2
import numpy as np
from loguru import logger


class MonitorClient:
    def __init__(self, width: int = 10, height: int = 10):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.width = width
        self.height = height

    def get_window_size(self, buffer: list[int]) -> Tuple[int, int]:
        return struct.unpack(">BBHH", buffer)[-2:]

    def connect(self, socket_path: str):
        self._sock.connect(socket_path)
        logger.debug("Connected to " + socket_path)
        data = self._sock.recv(6)
        self.width, self.height = self.get_window_size(data)
        logger.debug(f"Terminal size: {self.width}x{self.height}")

    def send_pixel(self, x: int, y: int, level: int):
        msg = struct.pack(">BBHH", 3, level, x, y)
        self._sock.sendall(msg)

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        img_resized = cv2.resize(
            image,
            (self.width, self.height),
            interpolation=cv2.INTER_AREA
        )
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        return gray

    def send_image(self, image: np.ndarray):
        start_time = datetime.datetime.now()
        prepared_image = self._prepare_image(image)
        prepared_time_ms = (datetime.datetime.now() - start_time).microseconds / 1000
        for y in range(len(prepared_image)):
            for x in range(len(prepared_image[0])):
                level = int(prepared_image[y, x])
                self.send_pixel(x, y, level)
        send_time_ms = (datetime.datetime.now() - start_time).microseconds / 1000
        logger.debug(f"Image sended (prep={prepared_time_ms}ms, sending={send_time_ms}ms)")

    def close(self):
        self._sock.close()
        logger.debug("Closing monitor client")