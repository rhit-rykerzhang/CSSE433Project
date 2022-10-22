import socket
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


# print(isOpen("433-34.csse.rose-hulman.edu", 10800))
def monitor_host():
    open = isOpen("433-34.csse.rose-hulman.edu", 27017)
    if open:
        print("It's running")
    else:
        print("It's down")
    threading.Timer(300, monitor_host).start()


class MyHandler(FileSystemEventHandler):
    def on_modified(self,  event):
        print(f'event type: {event.event_type} path : {event.src_path}')

    def on_created(self,  event):
        print(f'event type: {event.event_type} path : {event.src_path}')

    def on_deleted(self,  event):
        print(f'event type: {event.event_type} path : {event.src_path}')


if __name__ == "__main__":

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(
        event_handler,  path='/Users/IscoJ/Desktop/CSSE433Project/logs/tmp.log',  recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
# monitor_host()
