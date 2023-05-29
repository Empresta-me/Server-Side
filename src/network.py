from src.protocol import *
import json

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

    def calculate_reputation(self, observer_id : str, interest_dist : int) -> dict:

        # gets the index of the observer from the order
        observer_idx =self.ordered_nodes.index(observer_id)

        
        open_list = set([observer_idx]) # the nodes to be evaulated
        influence = [ [] for i in range(len(self.nodes))] # the forces influencing the score of each node
        nodes_depth = [ 1e7 for i in range (len(self.nodes)) ] # the minimum distance from the observer to each node


        # function that transforms the depth of the node to it's weight
        def weight(depth) -> float:
            return 2**(-depth)

        # helper recursive tree search function
        def recursive_propagate(idx : int, polarity : int = 0, prev_idxs : list = [], depth : int = 0, had_against : bool = False):

            # get the connections of this node
            connections = self.matrix[idx]

            # update the depth if necessary
            if depth < nodes_depth[idx]:
                nodes_depth[idx] = depth

            # for each connection...
            for other_idx, value in enumerate(connections):

                # ignore if it's not a connection
                if value == 0:
                    continue

                # there can only be one against connection in a chain. Stop if there's a second
                if value == -1 and had_against:
                    continue

                # prevents backtrack / stay in place
                if other_idx == idx or other_idx in prev_idxs:
                    continue
                
                polarity_send = polarity # polarity gets inverted after vouch againts
                against_send = had_against # if there has been a vouch against

                # if the polarity has not been set (that is, we're evaluating the observer node still)
                if polarity == 0:
                    polarity_send = value # we set the polarity as the connection
                elif value == -1:
                    polarity_send = -1
                    against_send = True

                # influence it with your vouch
                influence[other_idx].append( (depth, polarity_send) )

                # propagate further
                recursive_propagate(other_idx, polarity_send, prev_idxs + [idx], depth + 1, against_send)

        recursive_propagate(observer_idx)

        reputation_dict = {}

        # calculate the reputation score of nodes from their influences
        for idx, influences in enumerate(influence):

            if idx == observer_idx:
                continue

            # if there are influences
            if influences:

                # calculates a weighted average of the influences
                numerator = 0
                denominator = 0

                for depth, polarity in influences:
                    numerator += (1 if polarity > 0 else 0) * weight(depth)
                    #numerator += polarity * weight(depth)
                    denominator += weight(depth)
                
                score = float(numerator)/float(denominator)
                score *= weight(nodes_depth[idx] - 1) # apllies distance falloff
            else:
                reputation_dict[self.ordered_nodes[idx]] = None
                continue

            reputation_dict[self.ordered_nodes[idx]] = score

        return reputation_dict


    def gen_diagram(self, observer_id, interest_dist : int = 3):
        # if observer does not exist, don't bother
        if observer_id not in self.nodes.keys():
            #TODO: debug
            return None

        # get reputation dict
        reputation = self.calculate_reputation(observer_id, interest_dist)

        print('rep : ' + str(reputation))

        nodes = []
        links = []

        def get_name(name : str, observer : str) -> str:
            if name == observer:
                return "(You)"
            else:
                return name

        for idx, name in enumerate(self.ordered_nodes):
            node = {"name":get_name(name,observer_id),"reputation":reputation.get(name, '?'),"id":idx}

            if name == observer:
                node['is_observer'] = True

            nodes.append( node )

            connections = self.matrix[idx]

            for other_idx, value in enumerate(connections):
                if value == 0:
                    continue

                links.append({"source":get_name(name,observer_id),"target":get_name(self.ordered_nodes[other_idx], observer_id),"value":value})
            
        print({"nodes":nodes,"links":links})
        return {"nodes":nodes,"links":links}
