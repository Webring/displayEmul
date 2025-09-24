import argparse

import cv2

from monitor_client import MonitorClient

def parse_args():
    parser = argparse.ArgumentParser(description="Отправка на монитор изображения")

    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Путь к изображению"
    )

    parser.add_argument(
        "--sock",
        type=str,
        required=True,
        help="Путь к сокету"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    monitor_client = MonitorClient()
    monitor_client.connect(args.sock)

    image = cv2.imread(args.image)
    monitor_client.send_image(image)

    monitor_client.close()
