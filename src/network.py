from src.protocol import *
from src.redis_interface import Redis_interface

class Node:
    def __init__(self, id : str):
        self.id = id
        self.vouches = {}

    def vouch(self, other_id, polarity : bool, clock : int) -> None:
        """Vouch (for or against) a particular node."""

        # Cannot vouch for itself
        if self.id == other_id:
            return

        self.vouches[other_id] = polarity, clock

class Network:

    def __init__(self):
        # load from redis to memory
        self.nodes = {}

        self.ordered_nodes = []
        self.matrix = self.create_adjacency_matrix()

    def update(self):
        self.ordered_nodes = list(self.nodes) # updates ordered nodes
        self.matrix = self.create_adjacency_matrix()

    def new_vouch(self, msg):
        # TODO: add to redis

        sender_id = msg.sender
        receiver_id = msg.receiver
        clock = msg.clock
        polarity = msg.state == 'FOR' # TODO: account for neutral vouches
        polarity = False # TODO: remove this!!

        # gets the node or adds it if it does not already exists
        node = None
        if sender_id not in self.nodes.keys():
            # creates a new node
            node = Node(sender_id)
            self.nodes[node.id] = node
        else:
            node = self.nodes[sender_id]

        # creates the receiver if it does not exist
        if receiver_id not in self.nodes.keys():
            # creates a new node
            self.nodes[receiver_id] = Node(receiver_id)

        # if there is not already a vouch for the receiver, update it
        if receiver_id not in node.vouches.keys():
            node.vouch(receiver_id, polarity, msg.clock)
        # if already exists, only update if newer
        else:
            _, current_clock = node.vouches[receiver_id]

            if clock > current_clock:
                node.vouch(receiver_id, polarity, msg.clock)

        self.update()

    def create_adjacency_matrix(self) -> list:
        """Creates and adjancency matrix to be used by the tree search"""

        # creates an N*N matrix
        size = len(self.nodes)
        matrix = [[0 for i in range(size)] for j in range(size)]

        # goes through each node...
        for node_idx, node_id in enumerate(self.ordered_nodes):

            # ... and each vouch
            for other_id in self.nodes[node_id].vouches.keys():
                other_idx = self.ordered_nodes.index(other_id) # gets the idx from the ordered list

                # don't check for connections if already exists
                if matrix[node_idx][other_idx] != 0:
                    continue

                # if they vouch for each other...
                if self.has_positive_connection(node_id, other_id):
                    matrix[node_idx][other_idx] = 1
                    matrix[other_idx][node_idx] = 1
                # if they vouch against each other...
                elif self.has_negative_connection(node_id, other_id):
                    matrix[node_idx][other_idx] = -1
                    matrix[other_idx][node_idx] = -1

        #"""
        print('MATRIX')
        print(self.ordered_nodes)
        for i in range(size):
            for j in range(size):
                print('{:4}'.format(matrix[i][j]), end='')
            print()
        #"""

        return matrix

    def has_positive_connection(self, a_id, b_id) -> bool:
        """Returns whether a positive vouch connection exists between node A and B. A positive vouch connection is made if positive vouches are reciprocal."""

        # gets theid_order nodes associated with the id. Returns false if at least one of them does not exist
        if a_id in self.nodes:
            a = self.nodes[a_id]
        else:
            return False
        if b_id in self.nodes:
            b = self.nodes[b_id]
        else:
            return False

        # does A vouches for B...
        a_vouches_for = False
        if b_id in a.vouches.keys():
            polarity, _ = a.vouches[b_id]
            a_vouches_for = polarity

        # does B vouches for A
        b_vouches_for = False
        if a_id in b.vouches.keys():
            polarity, _ = b.vouches[a_id]
            b_vouches_for = polarity 

        # positive connections are made if A and B vouch for each other
        return a_vouches_for and b_vouches_for

    def has_negative_connection(self, a_id : int, b_id : int) -> bool:
        """Returns whether a negative vouch connection exists between node A and B. A negative vouch connection is made if at least one of them vouches against the other."""

        # gets the nodes associated with the id. Returns false if at least one of them does not exist
        if a_id in self.nodes:
            a = self.nodes[a_id]
        else:
            return False
        if b_id in self.nodes:
            b = self.nodes[b_id]
        else:
            return False

        # does A vouches for B...
        a_vouches_against = False
        if b_id in a.vouches.keys():
            polarity, _ = a.vouches[b_id]
            a_vouches_against = polarity == False

        # does B vouches for A
        b_vouches_against = False
        if a_id in b.vouches.keys():
            polarity, _ = b.vouches[a_id]
            b_vouches_against = polarity == False

        # negative vouch connections are made if at least one of them vouches against the other_id
        return a_vouches_against or b_vouches_against

    def gen_diagram(self, observer_id, interest_dist : int = 3):
        # if observer does not exist, don't bother
        if observer_id not in self.nodes.keys():
            #TODO: umcomment
            pass
            #return None

        def calculate_reputation(observer_id : str, interest_dist : int) -> dict:
            return {key:0.5 for key in self.nodes.keys()}

        reputation = calculate_reputation(observer_id, interest_dist)

        def name_with_rep(name) -> str:
            rep = reputation.get(name,None)

            if rep != None:
                return name + "\n" + str(100*rep)+"%"
            else:
                return name

        nodes = []
        links = []

        for idx, name in enumerate(self.ordered_nodes):
            nodes.append( {"name":f"{name_with_rep(name[0:4]+'...')}","id":idx} )

            connections = self.matrix[idx]

            for other_idx, value in enumerate(connections):
                if value == 0:
                    continue

                links.append({"source":f"{name_with_rep(name[0:4]+'...')}","target":f"{name_with_rep(self.ordered_nodes[other_idx][0:4]+'...')}","value":value})
            
        return {"nodes":nodes,"links":links}
