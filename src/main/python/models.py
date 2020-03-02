from PyQt5.QtCore import *
import web3
from web3.auto import w3

class NetworkConnector(QObject):
    
    # TODO Why static??!!
    on_connection_change = pyqtSignal()
    on_update = pyqtSignal()
    on_request = pyqtSignal(str, 'PyQt_PyObject', 'PyQt_PyObject')
    
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.web3 = web3.Web3()
        
        self.timer = QTimer()
        self.timer.setInterval( 5000 )
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
        
        def middleware_wrapper(make_request, w3):
            return lambda method, params: self.request_middleware(make_request, method, params)
        self.web3.middleware_onion.inject(middleware_wrapper, layer=0)
        
        self.endpoint_url = endpoint_url
        
        self._chain_id = chain_id or self.eth.chainId
        
        self.on_connection_change.emit()
        
    def disconnect(self):
        # TODO do it nicely in web3?
        self.web3 = web3.Web3()
        self.eth  = self.web3.eth
        self.on_connection_change.emit()

    @property
    def connected(self):
        return self.web3.isConnected()
    
    @property
    def block_number(self):
        #TODO generic cache-and-comparator!!
        return self.eth.blockNumber
    
    @property
    def chain_id(self):
        return self._chain_id
        
    def request_middleware(self, make_request, method, params):
        res = make_request(method, params)
        self.on_request.emit(method, params, res)
        return res

class AccountHolder(QObject):
    
    on_state_change = pyqtSignal()
    on_account_change = pyqtSignal()
    on_account_info_change = pyqtSignal()    

    def __init__(self, network_connector, parent = None):
        QObject.__init__(self, parent)
        
        self.address = None
        self.network_connector = network_connector
		
        self.network_connector.on_connection_change.connect(self.on_network_connection_change)
        self.network_connector.on_update.connect(self.on_network_update)

    def set_account(self, address):
        self.address = address
        self.on_account_change.emit()
    
    @property
    def active(self):
        return self.network_connector.connected
        
    def has_account(self):
        return self.address is not None
    
    def transaction_count(self):
        return self.network_connector.eth.getTransactionCount(self.address)
        
    def balance(self):
        return self.network_connector.eth.getBalance(self.address)

    ########
    
    def on_network_connection_change(self):
        self.on_state_change.emit()
    def on_network_update(self):
        if self.has_account():
            self.on_account_info_change.emit()

class Transaction:
    def __init__(self, _from, to, nonce, value = 0, gasLimit = 21000, gasPrice = 0, hash = ""):
        self._from = _from
        self.to = to
        self.nonce = nonce
        self.value = value
        self.gasLimit = gasLimit
        self.gasPrice = gasPrice
        self.hash = hash

    @property
    def gasTotal(self):
        return self.gasPrice * self.gasLimit

class Receipt:
    def __init__(self, block_number, transaction_index, gas_used, hash):
        self.block_number = block_number
        self.transaction_index = transaction_index
        self.gas_used = gas_used
        self.hash = hash

class Wallet(QObject):
	
    on_connection_change = pyqtSignal()
    on_account_change = pyqtSignal()
    on_pending_transaction_change = pyqtSignal()
            
    def __init__(self, network_connector, parent = None):
        
        QObject.__init__(self, parent)
        
        self.network_connector = network_connector
        
        self.private_key = None
        self.seed_phrase = None
		
        self.account_holder = AccountHolder(self.network_connector)
        self.pending_transaction = None
        self.receipt = None
    
        self.network_connector.on_connection_change.connect(self.on_network_connection_change)
        self.network_connector.on_update.connect(self.on_network_update)

    # TODO getters then setters everywhere!
    @property
    def connected(self):
        return self.network_connector.connected

    def has_account(self):
        return self.private_key is not None

    @property
    def account(self):
        return self.account_holder

    def set_account(self, private_key):
        self.private_key = private_key
        try: 
            address = w3.eth.account.privateKeyToAccount(web3.Web3.toBytes(hexstr=self.private_key)).address
        except:
            address = None
        self.account_holder.set_account(address)
        self.on_account_change.emit()
	
    def set_seed_phrase(seed_phrase):
        pass

    def send_transaction(self, to, value, gas_price):
        t = {
            "from": self.account.address,
            "to": to,
            "value": value,
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": self.account.transaction_count()
            #"data": data
        }
        signed = w3.eth.account.signTransaction(t, private_key=web3.Web3.toBytes(hexstr=self.private_key))
        raw = web3.Web3.toHex(signed.rawTransaction)
        hash = web3.Web3.toHex(self.network_connector.eth.sendRawTransaction(raw))
        self.receipt = None
        self.pending_transaction = Transaction(t["from"], t["to"], t["nonce"], t["value"], t["gas"], t["gasPrice"], hash)
        self.on_pending_transaction_change.emit()
		
	########
    
    def on_network_connection_change(self):
        self.on_connection_change.emit()
        
    def on_network_update(self):
        if self.pending_transaction and not self.receipt:
            try:
                r = self.network_connector.eth.getTransactionReceipt(self.pending_transaction.hash)
                self.receipt = Receipt(r['blockNumber'], r['transactionIndex'], r['cumulativeGasUsed'], web3.Web3.toHex(r["transactionHash"]))
                self.on_pending_transaction_change.emit()
            except:
                pass
