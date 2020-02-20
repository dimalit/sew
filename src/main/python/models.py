class Transaction:
	def __init__(self):
		self._from = None
		self.to = None
		self.nonce = None
		self.value = 0
		self.gasPrice = 0

class AccountInformer:
	def __init__(self):
		self.addess = None
		
		self.on_account_change = pyqtSignal()
		self.on_account_info_change = pyqtSignal()
		
	def set_account(self, address):
		pass

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
		
	
