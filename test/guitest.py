from slab import gui
from PyQt4 import Qt
from PyQt4 import Qwt5 as Qwt
from PyQt4.QtTest import QTest
from PyQt4 import uic
uifile = open("test_ui.py", 'w')
uic.compileUi("test.ui", uifile)
uifile.close()

from test_ui import *
import unittest
import time
import sys
import numpy as np



class GuiTest(unittest.TestCase):
    def setUp(self):
        self.app = Qt.QApplication([])
        self.win = TestWin()

    def tearDown(self):
        self.win._data_thread.exit()
        self.win.close()
        self.app.quit()

    def test_setupSlabWindow(self):
        self.assertEqual(self.win.data_thread_obj.thread(),
                         self.win._data_thread)
        self.win.params.update()
        self.assertDictContainsSubset({"rate":0.0},self.win.params)

    def test_updateParams(self):
        QTest.mouseDClick(self.win.param_rate, Qt.Qt.LeftButton)
        for _ in range(4):
            QTest.keyClick(self.win.param_rate, Qt.Qt.Key_Up)
        self.win.params.update()
        self.assertDictContainsSubset({"rate":4.},self.win.params)

    def test_multi_thread(self):
        t1 = time.time()
        QTest.mouseClick(self.win.go_button, Qt.Qt.LeftButton)
        QTest.mouseClick(self.win.abort_button, Qt.Qt.LeftButton)
        t2 = time.time()
        self.assertLess(t2 - t1, 1.0)

class ExistingAppTest(unittest.TestCase):
    existing_apps = ["scripts\\NWAWindow.pyw",
                     "instruments\\Alazar\\Scope2.py"]
    def test_app_startup(self):
        for file in self.existing_apps:
            pass

class test_DataThread(gui.DataThread):
    def clear(self):
        print "clear"
        self.gui["sine"].setData([],[])
        self.gui["cosine"].setData([],[])
        self.gui["qwtPlot"].replot()

    def run_script(self):
        omega = self.params["rate"]
        for i in range(100):
            self.progress(i, 100)
            if self.aborted():
                self.msg("aborted")
                break
            xrng = np.linspace(0, 2 * np.pi, num = i)
            time.sleep(.1)
            self.gui["sine"].setData(xrng, np.sin(omega * xrng))
            self.gui["cosine"].setData(xrng, np.cos(omega * xrng))
            self.gui["qwtPlot"].replot()


class TestWin(gui.SlabWindow, Ui_MainWindow):
    def __init__(self):
        gui.SlabWindow.__init__(self, test_DataThread, config_file=None)
        self.setupSlabWindow(autoparam=True)
        self.register_script("run_script", self.go_button, self.abort_button)
        self.abort_button.clicked.connect(self.test_clear)
        self.add_sweep_dialog()
        self.start_thread()
        self.sine = Qwt.QwtPlotCurve("Sine")
        self.cosine= Qwt.QwtPlotCurve("Cosine")
        self.sine.attach(self.qwtPlot)
        self.cosine.attach(self.qwtPlot)
        self.auto_register_gui()

    def test_clear(self):
        print "test_clear"
        self.emit(Qt.SIGNAL("RunOnDataThread"), "clear")

def show():
    sys.exit(gui.runWin(TestWin))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show()
    else:
        unittest.main()