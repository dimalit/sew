import ui
import models
import time

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QMainWindow()
    window.setWindowTitle("Simple Ethereum Wallet v0.1")
    
    wallet_widget = ui.WalletWidget()
    window.setCentralWidget(wallet_widget)
    
    nc = models.NetworkConnector()
    wallet = models.Wallet(nc)
    
    wallet_widget.network_widget.set_model(nc)
    wallet_widget.account_widget.connect_wallet(wallet)
    wallet_widget.transaction_widget.connect_wallet(wallet)
    wallet_widget.receipt_widget.connect_wallet(wallet)
    
    def print_request(method, params, res):
        print_res = res
        if "result" in res:
            print_res = res["result"]
        elif "error" in res:
            print_res = res["result"]
        print(method, str(params), "->", str(print_res))
    
    nc.on_request.connect(print_request)
    
    def log_request(method, params, res):
        print_res = res
        if "result" in res:
            print_res = res["result"]
        elif "error" in res:
            print_res = res["result"]
        wallet_widget.log_widget.append(f"{time.asctime()} {method} {str(params)} -> {str(print_res)}")        
    
    nc.on_request.connect(log_request)
    
    nc.connect("https://rpc.goerli.mudit.blog/") #"https://main-rpc.linkpool.io") #"http://127.0.0.1:1234")
    
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
