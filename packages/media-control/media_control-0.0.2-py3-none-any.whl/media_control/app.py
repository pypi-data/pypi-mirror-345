import io
import qrcode
import pyvolume
import pyautogui

import socket
from flask import Flask, render_template
from flask_socketio import SocketIO

class Utils:
    def getPORT(self, port=6968, max_port=65535 ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while port <= max_port:
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                port += 1
        raise IOError('no free ports')

    def getIPAddress(self):
        hostname = socket.getfqdn()
        IPAddr = socket.gethostbyname_ex(hostname)[2][1]
        return IPAddr

    def generateQRCode(self, data):
        qr = qrcode.QRCode()
        qr.add_data(data)
        f = io.StringIO()
        qr.print_ascii(out=f)
        f.seek(0)
        print(f.read())


class Routes:
    def index(self):
        return render_template("index.html")

    def play(self, data=None):
        pyautogui.press("space")

    def click(self, data=None):
        pyautogui.click()

    def move(self, data):
        sensitivity = float(data.get("sensitivity", 1))
        dx = float(data.get("dx")) * sensitivity
        dy = float(data.get("dy")) * sensitivity
        pyautogui.moveRel(dx, dy, 0.001)

    def volume(self, data):
        level = float(data.get("level"))
        pyvolume.custom(int(level))

    def keypress(self, data):
        if data is not None and "key" in data:
            if data["key"] == "Enter":
                pyautogui.press("enter")
            elif data["key"] == "Backspace":
                pyautogui.press("backspace")
            else:
                pyautogui.write(data["key"])


class MediaControl(Routes, Utils):
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO()
        self.socketio.init_app(self.app)
        
        self._setupRoutes()
    
    def _setupRoutes(self):
        self.app.route('/')(self.index)
        self.socketio.on("play")(self.play)
        self.socketio.on("click")(self.click)
        self.socketio.on("move")(self.move)
        self.socketio.on("volume")(self.volume)
        self.socketio.on("keypress")(self.keypress)

    def run(self):
        ipAddr = self.getIPAddress()
        port = self.getPORT()
        http_url = f"http://{ipAddr}:{port}"
        self.generateQRCode(http_url)

        self.socketio.run(self.app, host=ipAddr, port=port, debug=False)

if __name__ == "__main__":
    app = MediaControl()
    app.run()