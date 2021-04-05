import threading

class UsbDetector():
    def __init__(self):
        thread = threading.Thread(target=self._work)
        thread.daemon = True
        thread.start()
 
    def _work(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.monitor.start()
        for device in iter(self.monitor.poll, None):
            if device.action == 'add':
                self.on_created()
            else:
                self.on_deleted()
