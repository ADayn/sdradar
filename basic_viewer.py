import sys 
from PyQt4 import QtGui, uic, QtCore
import zmq
import numpy as np
import time
import pyqtgraph as pg

class MainWindow(QtGui.QMainWindow):
    def __init__(self, port ):
        super(MainWindow,self).__init__()
        uic.loadUi('simple.ui',self)
        self.show()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://192.168.1.20:%s"%str(port))
        self.socket.setsockopt(zmq.SUBSCRIBE,'')
        self.port = port

        self.worker = data_reader(self)
        self.connect(self.worker, self.worker.signal, self.update)
        self.run = 1
        self.worker.start()

    def update(self,data):
        self.graphicsView.clear()
        self.graphicsView.plot(np.abs(data))

    def closeEvent(self,event):
        self.run = 0

class data_reader(QtCore.QThread):
    def __init__(self,parent):
        QtCore.QThread.__init__(self,parent)
        self.signal = QtCore.SIGNAL("process")
        self.parent = parent
    def run(self):
        start = time.time()
        while self.parent.run == 1:
            tmp = self.parent.socket.recv()
            y = np.frombuffer(tmp)
            if time.time() - start > .05:
                start = time.time()
                self.emit(self.signal, np.fft.fft(y))

def main():
    argv = sys.argv
    if len(argv) < 2:
        raise ValueError("Please give the Sub port number as an arg")
    port = argv[1]
    app =  QtGui.QApplication(sys.argv)
    window = MainWindow(port)
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
