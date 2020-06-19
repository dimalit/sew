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
    wallet_widget.seed_dialog.set_model(wallet.seed)
    
    def apply_account(i):
        wallet.set_account(wallet.seed.get_key(i))
        
    wallet_widget.seed_dialog.on_accept.connect(apply_account)
    
    def print_request(method, params, res):
        print_res = res
        if "result" in res:
            print_res = res["result"]
        elif "error" in res:
            print_res = res["error"]
        print(method, str(params), "->", str(print_res))
    
    nc.on_request.connect(print_request)

    last_request = ""
    
    def log_request(method, params, res):
        
        global last_request
        
        print_res = res
        if "result" in res:
            print_res = res["result"]
        elif "error" in res:
            print_res = res["error"]
        
        was_max = wallet_widget.log_widget.verticalScrollBar().value() == wallet_widget.log_widget.verticalScrollBar().maximum()
        
        request = f"{method} {str(params)} -> {str(print_res)}"
        if request == last_request:
            wallet_widget.log_widget.undo()
        wallet_widget.log_widget.append(f"{time.asctime()} {request}")

        if was_max:
            wallet_widget.log_widget.verticalScrollBar().setValue( wallet_widget.log_widget.verticalScrollBar().maximum() )

        last_request = request
    
    nc.on_request.connect(log_request)
    
    nc.connect("https://rpc.goerli.mudit.blog/")
    #nc.connect("https://main-rpc.linkpool.io")
    #nc.connect("https://nodes.mewapi.io/rpc/eth) #"http://127.0.0.1:1234")
    
    # DEBUG window.setStyleSheet('QWidget:hover{ background-color: #f00; }')
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
