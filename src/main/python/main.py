import ui
import models

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QMainWindow()
    
    wallet = ui.WalletWidget()
    window.setCentralWidget(wallet)
    
    nc = models.NetworkConnector()
    wallet.network_widget.set_model(nc)
    nc.connect("http://127.0.0.1:1234")
    
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
