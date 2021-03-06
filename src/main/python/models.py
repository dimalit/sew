from PyQt5.QtCore import *
import web3
from web3.auto import w3
from pywallet import wallet
from pywallet.utils import *

import asyncio
from concurrent.futures import ThreadPoolExecutor

class NetworkConnector(QObject):
    
    # TODO Why static??!!
    on_connection_change = pyqtSignal()
    on_update = pyqtSignal()
    on_request = pyqtSignal(str, 'PyQt_PyObject', 'PyQt_PyObject')
    
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
       
        self.executor = ThreadPoolExecutor(10)
        asyncio.get_event_loop().set_default_executor(self.executor)
        
        self.web3 = web3.Web3()
        
        self.block_number = None    # main indicator of change
        
        self.timer = QTimer()
        self.timer.setInterval( 5000 )
        self.timer.timeout.connect(self.timer_handler)
        self.timer.start()

    def timer_handler(self):
        if not self.connected:
            return
        #block_number = self.eth.blockNumber
        loop = asyncio.get_event_loop()
        coro = loop.run_in_executor(None, lambda: self.eth.blockNumber)
        def cb(fut):
            block_number = fut.result()
            if self.block_number != block_number:
                self.block_number = block_number
                self.on_update.emit()
        asyncio.ensure_future(coro).add_done_callback(cb)

    def connect(self, endpoint_url, chain_id = None):
        # TODO why it's still 'connected' even if error?
        try:
            provider = web3.Web3.HTTPProvider(endpoint_url)
            self.web3 = web3.Web3(provider)
            self.eth  = self.web3.eth
            
            def middleware_wrapper(make_request, w3):
                return lambda method, params: self.request_middleware(make_request, method, params)
            self.web3.middleware_onion.inject(middleware_wrapper, layer=0)
            
            self.endpoint_url = endpoint_url
            
            self._chain_id = chain_id or self.eth.chainId
            self.block_number = self.eth.blockNumber
            
            self.on_connection_change.emit()
        except Exception as ex:
            print(ex)
        
    def disconnect(self):
        # TODO do it nicely in web3?
        self.web3 = web3.Web3()
        self.eth  = self.web3.eth
        self.on_connection_change.emit()

    @property
    def connected(self):
        return self.web3.isConnected()
    
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
        
    async def coro_transaction_count(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.network_connector.eth.getTransactionCount, self.address)
        
    def balance(self):
        return self.network_connector.eth.getBalance(self.address)

    async def coro_balance(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.network_connector.eth.getBalance, self.address)

    ########
    
    def on_network_connection_change(self):
        self.on_state_change.emit()
    def on_network_update(self):
        print("1")
        if self.has_account():
            self.on_account_info_change.emit()
        print("/1")

class SeedPhraseHolder(QObject):
    
    on_connection_change = pyqtSignal()
    on_params_change     = pyqtSignal()
    on_network_update    = pyqtSignal()
    
    def __init__(self, network_connector, parent = None):
        QObject.__init__(self, parent)
        self.network_connector = network_connector

        self.network_connector.on_connection_change.connect(lambda:self.on_connection_change.emit())
        self.network_connector.on_update.connect(lambda:self.on_network_update.emit())

        try:
            self.seed_phrase = "bitter age license pair key armed close about profit cruel fun tomato" # wallet.generate_mnemonic()
        except Exception as ex:
            pass

        try:
            self.derivation_path = "m/44'/60'/0'/0"
        except:
            pass
        
        self._address_count = 0
    
    @property
    def seed_phrase(self):
        return self._seed_phrase
        
    @seed_phrase.setter
    def seed_phrase(self, text):
        self.master_key = HDPrivateKey.master_key_from_mnemonic(text)
        self._seed_phrase = text
        self.on_params_change.emit()
    
    @property
    def derivation_path(self):
        return self._derivation_path
    
    @derivation_path.setter
    def derivation_path(self, text):
        #if self._derivation_path == text:
        #    return
        self.root_keys  = HDKey.from_path(self.master_key, text)
        self._derivation_path = text
        self.on_params_change.emit()
    
    @property
    def connected(self):
        return self.network_connector.connected
    
    def _find_addresses(self):
        
        self._address_count = 0        
        
        if not self.connected:
            return

        self._need_update = False

        i = 0
        found_empty = 0
        while True:
            addr = self.get_address(i)
            if self.network_connector.eth.getTransactionCount(addr) == 0:
                found_empty += 1
            else:
                found_empty = 0
                
            if found_empty == 2:
                self._address_count = i+1 - 1
                break

            i += 1
    
    async def _coro_find_addresses(self):
        return await asyncio.run_in_executor(None, self._find_addresses)
    
    def get_key(self, i):
        print(f"get key {i}")
        keys = HDKey.from_path(self.root_keys[-1],f'0/{i}')
        private_key = keys[-1]
        return private_key._key.to_hex()
        
    def get_address(self, i):
        keys = HDKey.from_path(self.root_keys[-1],f'0/{i}')
        private_key = keys[-1]
        address = web3.Web3.toChecksumAddress(private_key.public_key.address())
        return address
        
    def address_count(self):
        return self._address_count
        
    def get_balance(self, i):
        return self.network_connector.eth.getBalance(self.get_address(i))
        
    async def coro_get_balance(self, i):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_balance, i)
    

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
    
        self.seed_phrase_holder = SeedPhraseHolder(self.network_connector)
    
        self.network_connector.on_connection_change.connect(self.on_network_connection_change)
        self.network_connector.on_update.connect(self.on_network_update)

    # TODO getters then setters everywhere!
    @property
    def connected(self):
        return self.network_connector.connected

    def has_account(self):
        return self.account.has_account()

    @property
    def account(self):
        return self.account_holder
        
    @property
    def seed(self):
        return self.seed_phrase_holder

    def set_account(self, private_key):
        self.private_key = private_key
        print(f"PK {private_key}")
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
        try:
            signed = w3.eth.account.signTransaction(t, private_key=web3.Web3.toBytes(hexstr=self.private_key))
            raw = web3.Web3.toHex(signed.rawTransaction)
            hash = web3.Web3.toHex(self.network_connector.eth.sendRawTransaction(raw))
            self.receipt = None
            self.pending_transaction = Transaction(t["from"], t["to"], t["nonce"], t["value"], t["gas"], t["gasPrice"], hash)
            self.on_pending_transaction_change.emit()
        except Exception as ex:
            print(ex)
		
	########
    
    def on_network_connection_change(self):
        self.on_connection_change.emit()
        
    def on_network_update(self):
        print("3")
        if self.pending_transaction and not self.receipt:
            try:
                r = self.network_connector.eth.getTransactionReceipt(self.pending_transaction.hash)
                self.receipt = Receipt(r['blockNumber'], r['transactionIndex'], r['cumulativeGasUsed'], web3.Web3.toHex(r["transactionHash"]))
                self.on_pending_transaction_change.emit()
            except:
                pass
        print("/3")
