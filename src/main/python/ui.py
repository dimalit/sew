from PyQt5.QtWidgets import *

class AccountWidget(QGroupBox):
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
        
        self.setTitle(title or "Account:")
        
        self.layout = QGridLayout()
        
        self.private_key_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.transaction_count_edit = QLineEdit()
        self.balance_edit = QLineEdit()
        self.transaction_widget = TransactionWidget("Pending Transaction:")
        
        self.layout.addWidget(QLabel("Private Key:"), 0, 0)
        self.layout.addWidget(self.private_key_edit, 0, 1)
        self.layout.addWidget(QLabel("Address:"), 1, 0)
        self.layout.addWidget(self.address_edit, 1, 1)
        
        self.hor_layout = QHBoxLayout()
        self.hor_layout.addWidget(QLabel("Transaction Count:"))
        self.hor_layout.addWidget(self.transaction_count_edit)
        self.hor_layout.addWidget(QLabel("Balance:"))
        self.hor_layout.addWidget(self.balance_edit)
        self.hor_layout.addWidget(QLabel("ETH"))
        
        self.layout.addLayout(self.hor_layout, 2, 0, 1, 2)
        
        self.setLayout(self.layout)        

class TransactionWidget(QGroupBox):
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
        
        self.setTitle(title or "Transaction:")
        
        self.vert_layout = QVBoxLayout()
        
        self.from_edit = QLineEdit()
        self.to_edit = QLineEdit()
        self.value_edit = QLineEdit()
        self.gas_price_edit = QLineEdit()
        self.gas_amount_edit = QLineEdit()
        self.gas_total_edit = QLineEdit()
        self.total_edit = QLineEdit()
        
        self.addresses_layout = QHBoxLayout()
        self.addresses_layout.addWidget(QLabel("From:"))
        self.addresses_layout.addWidget(self.from_edit)
        self.addresses_layout.addWidget(QLabel("To:"))
        self.addresses_layout.addWidget(self.to_edit)
        self.addresses_layout.addWidget(QLabel("Value:"))
        self.addresses_layout.addWidget(self.value_edit)
        self.addresses_layout.addWidget(QLabel("ETH"))
                
        self.gas_layout = QHBoxLayout()
        self.gas_layout.addWidget(QLabel("Gas Limit:"))
        self.gas_layout.addWidget(self.gas_amount_edit)
        self.gas_layout.addWidget(QLabel("Gas Price:"))
        self.gas_layout.addWidget(self.gas_price_edit)
        self.gas_layout.addWidget(QLabel("Gas Total:"))
        self.gas_layout.addWidget(self.gas_total_edit)        
        self.gas_layout.addWidget(QLabel("ETH"))
        
        self.vert_layout.addLayout(self.addresses_layout)
        self.vert_layout.addLayout(self.gas_layout)
        
        self.setLayout(self.vert_layout)

class WalletWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.layout = QVBoxLayout()
        
        self.account_widget     = AccountWidget()
        self.transaction_widget = TransactionWidget("Pending Transaction:")
                
        self.layout.addWidget(self.account_widget)
        self.layout.addWidget(self.transaction_widget)
        
        self.setLayout(self.layout)
