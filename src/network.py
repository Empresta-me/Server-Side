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

    def add(self, msg):
        # TODO: add to redis

        # gets the node or adds it if it does not already exists
        sender_id = msg.sender
        receiver_id = msg.receiver
        clock = msg.clock
        polarity = msg.state == 'FOR' # TODO: account for neutral vouches

        node = None
        if sender_id not in self.nodes.keys():
            node = Node(sender_id)
            self.nodes[sender_id] = node
        else:
            node = self.nodes[sender_id]

        # if there is not already a vouch for the receiver, update it
        if receiver_id not in node.vouches.keys():
            node.vouch(receiver_id, polarity, msg.clock)
        # if already exists, only update if newer
        else:
            _, current_clock = node.vouches[receiver_id]

            if clock > current_clock:
                node.vouch(receiver_id, polarity, msg.clock)

    def gen_diagram(self, observer_id, interest_dist : int = 3):
        # if observer does not exist, don't bother
        if observer_id not in self.nodes.keys():
            return None

        def calculate_reputation(self, observer_id : str, interest_dist : int) -> dict:
            return {key:0.5 for key in self.nodes.keys()}

        reputation = calculate_reputation(observer_id, interest_dist)

        nodes = []
        links = []

        for name, rep in reputation:
            nodes.append( {"name":f"{name[0:4]}...","id":name} )

            # TODO: links

        return {"nodes":nodes,"links":links}
