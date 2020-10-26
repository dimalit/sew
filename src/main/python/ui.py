from asyncqt import asyncSlot

import asyncio

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import web3

class ApplyEditButton(QPushButton):
    
    Apply = 0
    Edit = 1
    
    def __init__(self, apply_text = "Apply", edit_text = "Edit", parent = None):
        QPushButton.__init__(self, parent)
        
        self.setText(apply_text)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

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
        self.apply_edit_button = ApplyEditButton("Connect", "Change")
        
        self.layout.addWidget(QLabel("Endpoint URL:"), 0, 0)
        self.layout.addWidget(self.endpoint_url_edit, 0, 1)
        self.layout.addWidget(QLabel("ChainID:"), 1, 0)
        self.layout.addWidget(self.chain_id_edit, 1, 1)
        self.layout.addWidget(QLabel("Current Block:"), 2, 0)
        self.layout.addWidget(self.block_no_edit, 2, 1)
        
        self.layout.addWidget(self.apply_edit_button, 0, 2, 3, 1)
                
        self.setLayout(self.layout)
        
        ########
        
        self.apply_edit_button.clicked.connect(self.apply_edit)
        
        ########
        
        self.chain_id_edit.setReadOnly(True)
        self.block_no_edit.setReadOnly(True)
        
    def set_model(self, model):
        #TODO assert("model" not in self)
        self.model = model
        model.on_connection_change.connect(self.show_state)
        model.on_update.connect(self.show_data)
        
    def show_state(self):
        self.endpoint_url_edit.setReadOnly(self.model.connected)
        if self.model.connected:
            self.endpoint_url_edit.setText(self.model.endpoint_url)
            self.chain_id_edit.setText(str(self.model.chain_id))
            self.chain_id_edit.setEnabled(True)
            self.block_no_edit.setEnabled(True)
            self.apply_edit_button.setState(ApplyEditButton.Edit)
            
            self.show_data()
        else:
            self.endpoint_url_edit.selectAll()
            self.chain_id_edit.setText("")
            self.block_no_edit.setText("")
            self.chain_id_edit.setEnabled(False)
            self.block_no_edit.setEnabled(False)
            self.apply_edit_button.setState(ApplyEditButton.Apply)
    
    def show_data(self):
        self.block_no_edit.setText(str(self.model.block_number))
        
    def apply_edit(self):
        if self.model.connected:
            self.model.disconnect()
        else:
            self.model.connect(self.endpoint_url_edit.text())

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
        self.apply_edit_button = ApplyEditButton("Apply", "Change")
        self.test_button = QPushButton("test")

        self.seed_dialog = SeedPhraseDialog(parent)
        
        self.show_seed_dialog_action = self.private_key_edit.addAction(self.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton), QLineEdit.TrailingPosition)
        
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
        
        self.layout.addWidget(self.apply_edit_button, 0, 2, 2, 1)
        self.layout.addWidget(self.test_button, 2, 2, 1, 1)
        
        self.setLayout(self.layout)
        
        ########
        
        self.apply_edit_button.clicked.connect(self.apply_edit)
        self.test_button.clicked.connect(self.test)
        self.private_key_edit.setText('0x1af84ac2809b41314a7454b65f692cabbe39f78007fd0134c0018fbb68c173f0')
        self.show_seed_dialog_action.triggered.connect(self._show_seed_dialog)
        self.seed_dialog.on_accept.connect(lambda i: self.private_key_edit.setText(self.wallet.seed.get_key(i)))
        
        ########
        
        self.address_edit.setReadOnly(True)
        self.transaction_count_edit.setReadOnly(True)
        self.balance_edit.setReadOnly(True)
        self.show_seed_dialog_action.setEnabled(False)

    def _show_seed_dialog(self):
        choice = -1
        for i in range(self.wallet.seed.address_count()):
            if self.wallet.seed.get_key(i) == self.private_key_edit.text():
                choice = i
        self.seed_dialog.current_choice = choice
        self.seed_dialog.show()

    def connect_wallet(self, wallet):
        self.wallet = wallet
        self.seed_dialog.set_model(wallet.seed)
        
        self.wallet.on_connection_change.connect(self.show_state)
        self.wallet.on_account_change.connect(self.show_account)
        self.wallet.account.on_account_info_change.connect(self.show_account_data)
        
        self.show_state()
        self.show_account()
        if wallet.has_account():
            self.show_account_data()
        
    def show_state(self):
        self.setEnabled(self.wallet.connected)
    
    def show_account(self):
        if self.wallet.has_account():
            self.private_key_edit.setReadOnly(True)
            self.apply_edit_button.setState(self.apply_edit_button.Edit)
            
            self.private_key_edit.setText(self.wallet.private_key)
            self.address_edit.setText(self.wallet.account.address)
        else:
            self.address_edit.setText("")
            self.private_key_edit.setReadOnly(False)
            self.apply_edit_button.setState(self.apply_edit_button.Apply)

        self.show_seed_dialog_action.setEnabled(not self.wallet.has_account())
        self.show_account_data()
        
    def show_account_data(self):
        holder = self.wallet.account
        
        if holder.has_account():
            asyncio.ensure_future( holder.coro_transaction_count() ).add_done_callback(lambda fut: self.transaction_count_edit.setText(str(fut.result())))
            asyncio.ensure_future( holder.coro_balance() ).add_done_callback(lambda fut: self.balance_edit.setText(str(fut.result()/1e+18)))
            #cnt = await holder.coro_transaction_count()
            #self.transaction_count_edit.setText(str(cnt))
            #balance = await holder.coro_balance()
            #self.balance_edit.setText(str(balance/1e+18))
        else:
            self.transaction_count_edit.setText("")
            self.balance_edit.setText("")

    def test(self):
        self.show_account_data()    

    def apply_edit(self):
        if self.wallet.has_account():
            self.wallet.set_account(None)
        else:
            private_key = self.private_key_edit.text()
            self.wallet.set_account(private_key)

class TransactionWidget(QGroupBox):
    
    on_editing_change = pyqtSignal()
    
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
                
        self.setTitle(title or "Transaction:")
        
        self.vert_layout = QGridLayout()
        
        self.from_edit = QLineEdit()
        self.to_edit = QLineEdit()
        self.value_edit = QLineEdit()
        self.gas_price_edit = QLineEdit()
        self.gas_amount_edit = QLineEdit()
        self.gas_total_edit = QLineEdit()
        self.total_edit = QLineEdit()
        self.hash_edit = QLineEdit()
        self.apply_edit_button = ApplyEditButton("Sign && Send", "New")        
        
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
        
        self.vert_layout.addLayout(self.addresses_layout, 0, 0)
        self.vert_layout.addLayout(self.gas_layout, 1, 0)
        self.vert_layout.addLayout(self.hash_layout, 2, 0)
        
        self.vert_layout.addWidget(self.apply_edit_button, 0, 1, 3, 1)        
        
        self.setLayout(self.vert_layout)
        
        ########
        
        self.apply_edit_button.clicked.connect(self.apply_edit)
        self.to_edit.setText("0x00Dd2088723141852C65F93d789F58269A6ffAEe")
        self.value_edit.setText("0.001")
        self.gas_price_edit.setText("1e-9")
        self.gas_amount_edit.setText("21000")
        
        ########
        
        self.from_edit.setReadOnly(True)
        self.hash_edit.setReadOnly(True)
        self.gas_total_edit.setReadOnly(True)
        self.total_edit.setReadOnly(True)
        self.gas_amount_edit.setReadOnly(True)
        
        self.set_editing(True)
        
    def connect_wallet(self, wallet):
        self.wallet = wallet
        
        self.wallet.on_connection_change.connect(self.show_state)
        self.wallet.on_account_change.connect(self.show_state)
        self.wallet.on_pending_transaction_change.connect(self.show_transaction)
        
        self.show_state()
#        self.show_transaction()
    
    def set_editing(self, value):
        
        self.editing = value
        
        if self.editing:
            self.to_edit.setReadOnly(False)
            self.value_edit.setReadOnly(False)
            self.gas_price_edit.setReadOnly(False)
            
            self.hash_edit.setText("")
            self.gas_total_edit.setText("")
            self.total_edit.setText("")
            self.apply_edit_button.setState(ApplyEditButton.Apply)
        else:
            self.to_edit.setReadOnly(True)
            self.value_edit.setReadOnly(True)
            self.gas_price_edit.setReadOnly(True)

            self.apply_edit_button.setState(ApplyEditButton.Edit)
            
        self.on_editing_change.emit()
    
    def show_state(self):
        if (not self.wallet.connected) or (not self.wallet.has_account()):
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            self.from_edit.setText(self.wallet.account.address)
    
    def show_transaction(self):
        
        t = self.wallet.pending_transaction

        if t is not None:
            self.set_editing(False)
            
            self.from_edit.setText(t._from)
            self.to_edit.setText(t.to)
            self.value_edit.setText(str(t.value/1e+18))
            self.gas_amount_edit.setText(str(t.gasLimit))
            self.gas_price_edit.setText(str(t.gasPrice/1e+18))
            self.gas_total_edit.setText(str(t.gasTotal/1e+18))
            self.hash_edit.setText(t.hash or "")
        else:
            self.set_editing(True)
            
            self.from_edit.setText("")
            self.to_edit.setText("")
            self.value_edit.setText("")
            self.gas_amount_edit.setText("")            
            self.gas_price_edit.setText("")
            self.gas_total_edit.setText("")
            self.total_edit.setText("")
            self.hash_edit.setText("")
        
    def apply_edit(self):
        if self.apply_edit_button.state == ApplyEditButton.Apply:
            try:
                to = self.to_edit.text()
                if not web3.Web3.isChecksumAddress(to):
                    raise RuntimeError(f"Invalid address: {to}")
                value = int(float(self.value_edit.text())*1e+18)
                gas_price = int(float(self.gas_price_edit.text())*1e+18)
                self.wallet.send_transaction(to, value, gas_price)
            except Exception as ex:
                print(ex)
        elif self.apply_edit_button.state == ApplyEditButton.Edit:
            self.set_editing(True)

class ReceiptWidget(QGroupBox):
    def __init__(self, title = "", parent = None):
        QGroupBox.__init__(self, parent)
        
        self.setTitle(title or "Receipt:")
        
        self.vert_layout = QVBoxLayout()
        
        self.block_no_edit = QLineEdit()
        self.tx_no_edit = QLineEdit()
        self.gas_used_edit = QLineEdit()
        
        self.explorer_link = QLabel();
        self.explorer_link.openExtarnalLinks = True
        
        
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
        
        ########

        self.block_no_edit.setReadOnly(True)
        self.tx_no_edit.setReadOnly(True)
        self.gas_used_edit.setReadOnly(True)
        
    def connect_wallet(self, wallet):
        self.wallet = wallet
        
        self.wallet.on_connection_change.connect(self.show_state)
        self.wallet.on_account_change.connect(self.show_state)
        self.wallet.on_pending_transaction_change.connect(self.show_transaction)
        
        self.show_state()
        self.show_transaction()
        
    def show_state(self):
        self.setEnabled(self.wallet.connected and self.wallet.account.has_account() and self.wallet.receipt is not None)
        
    def show_transaction(self):
        r = self.wallet.receipt
        if r:
            self.block_no_edit.setText(str(r.block_number))
            self.tx_no_edit.setText(str(r.transaction_index))
            self.gas_used_edit.setText(str(r.gas_used))
            self.explorer_link.setText(f"<a href='https://goerli.etherscan.io/tx/{r.hash}'>https://goerli.etherscan.io/tx/{r.hash}</a>")
            
            self.setEnabled(True)
        else:
            self.block_no_edit.setText("")
            self.tx_no_edit.setText("")
            self.gas_used_edit.setText("")
            self.explorer_link.setText("")
            
            self.setEnabled(False)

class SeedPhraseDialog(QDialog):
    
    on_accept = pyqtSignal(int)
    
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        
        self.layout = QGridLayout()
        
        self.seed_phrase_edit  = QLineEdit()
        self.der_path_edit     = QLineEdit()
        self.addresses_layout  = QVBoxLayout()
        self.addresses_widget  = QWidget()
        self.buttons           = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.layout.addWidget(QLabel("Seed Phrase:"), 0, 0)
        self.layout.addWidget(self.seed_phrase_edit, 1, 0, 1, 2)
        self.seed_phrase_edit.setMinimumWidth(500)
        self.layout.addWidget(QLabel("Derivation Path:"), 2, 0)
        self.layout.addWidget(self.der_path_edit, 2, 1)
        
        scroll_area = QScrollArea()
        self.addresses_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.addresses_widget.setLayout(self.addresses_layout)
        scroll_area.setWidget(self.addresses_widget)
        self.layout.addWidget(scroll_area, 3, 0, 1, 2)
        #self.layout.addWidget(self.addresses_widget, 3, 0, 1, 2)
        
        self.layout.addWidget(self.buttons, 4, 0, 1, 2)
        
        self.setLayout(self.layout)
        
        ########
        
        self.seed_phrase_edit.textChanged.connect(self.apply_changes)
        self.der_path_edit.textChanged.connect(self.apply_changes)
        self.buttons.accepted.connect(self.accept_choice)
        self.buttons.rejected.connect(self.reject_choice)
        
    ########
        
    def apply_changes(self):
        seed = self.seed_phrase_edit.text()
        der_path = self.der_path_edit.text()
        try:
            self.model.seed_phrase = seed
            self.model.derivation_path = der_path
        except Exception as ex:
            print(str(ex))
    
    ########
    
    def set_model(self, holder):
        self.model = holder
        
        self.model.on_connection_change.connect(self.show_state)
        self.model.on_params_change.connect(self.show_params)
        self.model.on_network_update.connect(self.show_details)
        
        self.show_state()
        
    def show_state(self):
        self.show_params()

    def show_params(self):
        self.seed_phrase_edit.setText(self.model.seed_phrase)
        self.der_path_edit.setText(self.model.derivation_path)
        self.show_details()
        
    def show_details(self):
        cnt = self.model.address_count()
        if cnt == self.addresses_layout.count():
            return
        
        for i in range(cnt):
            address = self.model.get_address(i)
            balance = self.model.network_connector.eth.getBalance(address) / 1e18
            item = QRadioButton(f"{address} ({balance} ETH)")
            self.addresses_layout.addWidget(item)
        self.addresses_widget.adjustSize()

    ########
    
    @property
    def current_choice(self):
        for i in range(self.model.address_count()):
            if self.addresses_layout.itemAt(i).widget().isChecked():
                return i
        return None
    
    @current_choice.setter
    def current_choice(self, ii):
        for i in range(self.model.address_count()):
            if i == ii:
                self.addresses_layout.itemAt(i).widget().setChecked(True)
            else:
                self.addresses_layout.itemAt(i).widget().setChecked(False)

    def accept_choice(self):
        self.setVisible(False)
        self.on_accept.emit(self.current_choice)
    
    def reject_choice(self):
        self.setVisible(False)
                

class WalletWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.layout = QGridLayout()

        self.network_widget     = NetworkWidget()
        self.account_widget     = AccountWidget()
        self.transaction_widget = TransactionWidget("Pending Transaction:")
        self.receipt_widget     = ReceiptWidget()
        self.log_widget         = QTextEdit()
        
        self.log_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        self.layout.addWidget(self.network_widget, 0, 0)
        self.layout.addWidget(self.account_widget, 1, 0)
        self.layout.addWidget(self.transaction_widget, 2, 0)
        self.layout.addWidget(self.receipt_widget, 3, 0)
        self.layout.addWidget(self.log_widget, 4, 0)
        
        self.setLayout(self.layout)
        
