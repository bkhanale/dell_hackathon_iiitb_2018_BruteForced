import threading
import pickle
import atexit
import time
import json
import requests

from hashlib import sha256
from flask import Flask, request

from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM

xpro = ""
ysupp = ""


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        """
        A function that returns the hash of the block contents.
        """
        block_string = json.dumps(
            obj=self.__dict__,
            sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


def proof_of_work(block):
    """
    Function that tries different values of nonce to get a hash
    that satisfies our difficulty criteria.
    """
    block.nonce = 0

    computed_hash = block.compute_hash()
    while not computed_hash.startswith('0' * Blockchain.difficulty):
        block.nonce += 1
        computed_hash = block.compute_hash()

    return computed_hash


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # Remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash)
        proof = proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        # Announce it to the network
        announce_new_block(new_block)
        return new_block.index


# Endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
def new_transaction(tx_data):
    required_fields = ["user_name", "text", "time"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invlaid transaction data"
    blockchain[xpro][ysupp].add_new_transaction(tx_data)
    return "Success"


# Endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
def get_chain():
    # make sure we've the longest chain
    #consensus()
    chain_data = []
    for block in blockchain[xpro][ysupp].chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


# Endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
def mine_unconfirmed_transactions():
    result = blockchain[xpro][ysupp].mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


# Endpoint to add new peers to the network.
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid data"
    for node in nodes:
        peers.add(node)
    return "Success"


# Endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(
        index=block_data["index"],
        transactions=block_data["transactions"],
        timestamp=block_data["timestamp"],
        previous_hash=block_data["previous_hash"])
    proof = block_data['hash']
    added = blockchain[xpro][ysupp].add_block(block, proof)
    if not added:
        return "The block was discarded by the node"
    return "Block added to the chain"


# Endpoint to query unconfirmed transactions
def get_pending_tx():
    return json.dumps(blockchain[xpro][ysupp].unconfirmed_transactions)


def consensus():
    """
    Our simple consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain[xpro][ysupp].chain)
    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain[xpro][ysupp].check_chain_validity(chain):
            current_len = length
            longest_chain = chain
    if longest_chain:
        blockchain[xpro][ysupp] = longest_chain
        return True
    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(
            url=url,
            data=json.dumps(
                obj=block.__dict__,
                sort_keys=True))


def log(msg):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(
        '%s:   %s :%s ' %
        (current_time,
         threading.current_thread().getName(),
         msg))


def accept_incoming_connections(clients_list_lock):
    while True:
        try:
            client, client_address = SERVER.accept()
            log("%s:%s has connected." % client_address[:])
            addresses[client] = client_address
            threading.Thread(
                target=handle_client,
                args=(
                    client,
                    clients_list_lock,
                ),
                name='client %s:%s thread' %
                client_address[:]).start()
        except Exception as err:
            log('error in accept_incoming_connections: %s' % err)
            break
    SERVER.close()


def create_server_json_msg(text):
    server_msg = create_json_msg(user_name='Server',
                                 text=text)
    return server_msg


def create_json_msg(user_name, text):
    sending_time = time.strftime("%H:%M", time.localtime())
    new_msg = {
        'user_name': user_name,
        'text': text,
        'time': sending_time
    }
    return new_msg


def handle_client(client, clients_list_lock):
    global xpro
    global ysupp
    log('Start thread for this client')
    incoming_msg = pickle.loads(client.recv(BUFSIZ))
    log('Server receive register message \n %s' % incoming_msg)
    welcome = 'Welcome %s! If you ever want to quit,' \
              ' type {quit} to exit\n' % incoming_msg['user_name']
    welcome_msg = create_server_json_msg(text=welcome)
    client.send(bytes(pickle.dumps(welcome_msg)))
    log('Send to %s \n msg= %s' % (client.getsockname(), welcome_msg))
    has_join = "%s has joined the chat!\n" % incoming_msg['user_name']
    has_join_msg = create_server_json_msg(has_join)
    broadcast(has_join_msg, clients_list_lock)
    with clients_list_lock:
        clients[client] = incoming_msg['user_name']
    while True:
        try:
            incoming_msg = client.recv(BUFSIZ)
            incoming_msg = pickle.loads(incoming_msg)
        except EOFError:  # Possibly client has left brutality the chat.
            if incoming_msg.decode("utf8") == '':
                incoming_msg = {
                    'text': "{quit}\n"  # Back to safety quit scenario
                }
        if incoming_msg['text'] != "{quit}\n":
            log('Incoming message from %s \n message = %s'
                % (client.getsockname(), incoming_msg))
            log('Broadcasting the message')
            xpro = int(incoming_msg['producerID'][-1]) - 1
            ysupp = int(incoming_msg['supplierID'][-1]) - 1
            log(new_transaction(incoming_msg))
            log(mine_unconfirmed_transactions())
            log(get_chain())
            broadcast(incoming_msg, clients_list_lock)
        else:
            log('Client %s:%s has disconnected' % client.getsockname())
            left_client = client.getsockname()
            with clients_list_lock:
                client.close()
                log('client %s:%s deleted' % left_client)
                has_left = "%s has left the chat.\n" % clients[client]
                del clients[client]
            has_left_msg = create_server_json_msg(has_left)
            log('Broadcasting message %s' % has_left[:-2])
            broadcast(has_left_msg, clients_list_lock)
            break
    log('thread is finished')


def broadcast(msg, clients_list_lock):
    log('Start broadcasting \n %s' % msg)
    msg = bytes(pickle.dumps(msg))
    with clients_list_lock:
        for sock in clients:
            sock.send(msg)
            log('sent to %s:%s' % sock.getsockname())
    log('Finish broadcasting')


def close_server(clients_list_lock):
    with clients_list_lock:
        log('Closing the server')
        SERVER.close()
    log('Server is closed')


def get_my_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # I know this is a hack but it is the shortest way.
    my_ip = (s.getsockname()[0])
    s.close()
    return my_ip


def start_listen():
    tries = 0
    while True:
        try:
            SERVER.bind(ADDR)
            break
        except OSError as e:
            # Address in use, if server recovers it happens
            if e.errno == 48:
                print('Address in use try to reconnect in 10 seconds')
                time.sleep(10)
                tries += 1
                if tries > 1:
                    print('Address is in use for more than 30 seconds, exit program')
                    exit(0)
            pass


HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
clients = {}
addresses = {}
start_listen()
local_ip = get_my_ip()
clients_list_lock = threading.Lock()
SERVER.listen(50)  # Listens for 50 connections at max.
atexit.register(close_server, clients_list_lock=clients_list_lock)
print("Server is listnening on %s" % local_ip)
# The node's copy of blockchain
blockchain = [[Blockchain() for x in range(3)] for y in range(2)]
# The address to other participating members of the network
peers = set()
ACCEPT_THREAD = threading.Thread(
    target=accept_incoming_connections,
    args=(clients_list_lock,),
    name='accept_connections_thread')
ACCEPT_THREAD.start()  # Starts the infinite loop.
ACCEPT_THREAD.join()
