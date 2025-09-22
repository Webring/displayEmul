import cv2

from monitor_client import MonitorClient

if __name__ == "__main__":
    monitor_client = MonitorClient()
    monitor_client.connect("/tmp/monitor.sock")

    monitor_client.send_image(cv2.imread("img_2.png"))

    monitor_client.close()
