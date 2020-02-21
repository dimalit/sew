from PyQt5.QtWidgets import *

class ApplyEditButton(QPushButton):
    
    Apply = 0
    Edit = 1
    
    def __init__(self, apply_text = "Apply", edit_text = "Edit", parent = None):
        QPushButton.__init__(self, parent)
        
        self.setText(apply_text)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.apply_text = apply_text
        self.edit_text = edit_text
        self.state = self.Apply

        
    def setState(self, state):
        assert(state == self.Apply or state == self.Edit)
        self.state = state
        if self.state == self.Apply:
            self.setText(self.apply_text)
        elif self.state == self.Edit:
            self.setText(self.edit_text)

    def setApplyText(self, text):
        self.apply_text = text
        if self.state == self.Apply:
            self.setText(self.apply_text)
            
    def setEditText(self, text):
        self.edit_text = text
        if self.state == self.Edit:
            self.setText(self.edit_text)

class NetworkWidget(QGroupBox):
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
        
        self.setTitle(title or "Network:")
        
        self.layout = QGridLayout()
        
        self.endpoint_url_edit = QLineEdit()
        self.chain_id_edit = QLineEdit()
        self.block_no_edit = QLineEdit()
        
        self.layout.addWidget(QLabel("Endpoint URL:"), 0, 0)
        self.layout.addWidget(self.endpoint_url_edit, 0, 1)
        self.layout.addWidget(QLabel("ChainID:"), 1, 0)
        self.layout.addWidget(self.chain_id_edit, 1, 1)
        self.layout.addWidget(QLabel("Current Block:"), 2, 0)
        self.layout.addWidget(self.block_no_edit, 2, 1)
                
        self.setLayout(self.layout)        

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
        self.hash_edit = QLineEdit()
        
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
        
        self.hash_layout = QHBoxLayout()
        self.hash_layout.addWidget(QLabel("Hash"))
        self.hash_layout.addWidget(self.hash_edit)
        
        self.vert_layout.addLayout(self.addresses_layout)
        self.vert_layout.addLayout(self.gas_layout)
        self.vert_layout.addLayout(self.hash_layout)
        
        self.setLayout(self.vert_layout)

class ReceiptWidget(QGroupBox):
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
        
        self.setTitle(title or "Receipt:")
        
        self.vert_layout = QVBoxLayout()
        
        self.block_no_edit = QLineEdit()
        self.tx_no_edit = QLineEdit()
        self.gas_used_edit = QLineEdit()
        self.explorer_link = QLabel();
        
        self.location_layout = QHBoxLayout()
        self.location_layout.addWidget(QLabel("Block No:"))
        self.location_layout.addWidget(self.block_no_edit)
        self.location_layout.addWidget(QLabel("Transaction No:"))
        self.location_layout.addWidget(self.tx_no_edit)
        self.location_layout.addWidget(QLabel("Cumulative Gas Used:"))
        self.location_layout.addWidget(self.gas_used_edit)
        
        self.link_layout = QHBoxLayout()
        self.link_layout.addWidget(self.explorer_link)
        
        self.vert_layout.addLayout(self.location_layout)
        self.vert_layout.addLayout(self.link_layout)
        
        self.setLayout(self.vert_layout)

class WalletWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.layout = QGridLayout()
        
        self.network_apply_edit_button = ApplyEditButton("Connect", "Change")
        self.account_apply_edit_button = ApplyEditButton("Apply", "Change")
        self.transaction_apply_edit_button = ApplyEditButton("Sign && Send", "Change")

        self.network_widget      = NetworkWidget()
        self.account_widget     = AccountWidget()
        self.transaction_widget = TransactionWidget("Pending Transaction:")
        self.receipt_widget     = ReceiptWidget()
        
        self.layout.addWidget(self.network_widget, 0, 0)
        self.layout.addWidget(self.network_apply_edit_button, 0, 1)
        self.layout.addWidget(self.account_widget, 1, 0)
        self.layout.addWidget(self.account_apply_edit_button, 1, 1)
        self.layout.addWidget(self.transaction_widget, 2, 0)
        self.layout.addWidget(self.transaction_apply_edit_button, 2, 1)
        self.layout.addWidget(self.receipt_widget, 3, 0)
        
        self.setLayout(self.layout)
