import ui
import models

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QMainWindow()
    
    wallet_widget = ui.WalletWidget()
    window.setCentralWidget(wallet_widget)
    
    nc = models.NetworkConnector()
    wallet = models.Wallet(nc)
    
    wallet_widget.network_widget.set_model(nc)
    wallet_widget.account_widget.connect_wallet(wallet)
    
    nc.connect("https://main-rpc.linkpool.io") #"http://127.0.0.1:1234")
    
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
