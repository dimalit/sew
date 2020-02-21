from PyQt5.QtCore import *
import web3

class NetworkConnector(QObject):
    
    # TODO Why static??!!
    on_connection_change = pyqtSignal()
    on_update = pyqtSignal()
    
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.web3 = web3.Web3()
        
        self.timer = QTimer()
        self.timer.setInterval( 1000 )
        self.timer.timeout.connect(self.timer_handler)
        self.timer.start()

    def timer_handler(self):
        if not self.connected:
            return
        self.on_update.emit()

    def connect(self, endpoint_url, chain_id = None):
        # TODO why it's still 'connected' even if error?
        provider = web3.Web3.HTTPProvider(endpoint_url)
        self.web3 = web3.Web3(provider)
        self.eth  = self.web3.eth
        
        self.endpoint_url = endpoint_url
        
        self._chain_id = chain_id or self.eth.chainId
        
        self.on_connection_change.emit()

    @property
    def connected(self):
        return self.web3.isConnected()
    
    @property
    def block_number(self):
        return self.eth.blockNumber
    
    @property
    def chain_id(self):
        return self._chain_id
        

class AccountInformer:
	def __init__(self):
		self.addess = None
		
		self.on_account_change = pyqtSignal()
		self.on_account_info_change = pyqtSignal()
		
	def set_account(self, address):
		pass

class Transaction:
	def __init__(self):
		self._from = None
		self.to = None
		self.nonce = None
		self.value = 0
		self.gasPrice = 0

class Wallet:
	
	def __init__(self):
		self.private_key = None
		self.address = None
		self.seed_phrase = None
		
		self.account_informer = AccountInformer()
		
		self.pending_transaction = None
		
		self.on_pending_transaction_change = pyqtSignal()
		
	def set_account(self, arg1, private_key, address):
		pass
	
	def set_seed_phrase(seed_phrase):
		pass
		
	def get_balance(self):
		pass
		
	def get_transaction_count(self):
		pass

	def send_transaction(self, to, value, gas_price):
		pass
		
	
