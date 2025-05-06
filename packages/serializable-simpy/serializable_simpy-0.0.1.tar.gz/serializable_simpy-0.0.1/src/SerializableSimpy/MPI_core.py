import math
import time
from mpi4py import MPI
from typing import Dict, List, Optional

from SerializableSimpy.core import Environment, Store
from SerializableSimpy.MPI_utils import scattering_stores, broadcast_stores, aggregate_stores, StoreMPI

class MPIGlobalEnv:
    def __init__(self, initial_time: float = 0.0):
        self.initial_time = initial_time
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        self.master_rank2stores = {}  # rank -> {"in":["store1", "store2", ...],"out":[]}
        #self.master_stores2rank= {}

        self.worker_in: Dict[str, StoreMPI] = {}
        self.worker_out: Dict[str, StoreMPI] = {}

        self.local_env: Optional[Environment] = None
        if self.rank>0:
            self.local_env = Environment()

    def process(self, p ):
        self.local_env.process(p)

    def inout_init(self, inout_stores: Optional[Dict[str, List[Store]]]=None):
        """
        Register an environment (producer, consumer, or both).
        On rank 0, this defines the global store communication graph.
        On workers, this registers the local environment and its input/output stores.
        """

        if self.rank == 0:
            self.master_rank2stores={}
            # e.g. {1: {'in': [], 'out': ['buffer']}, 2: {'in': ['buffer'], 'out': ['consumed']}}
            for i in range(1, self.size):
                neigh = self.comm.recv(source=i)
                self.master_rank2stores.update(neigh)

            self.master_stores2rank = {}
            for rank, stores in self.master_rank2stores.items():
                for direction, store_names in stores.items():
                    opposite = "out" if direction == "in" else "in" # Build the inverted mapping
                    for store in store_names:
                        if store not in self.master_stores2rank:
                            self.master_stores2rank[store] = {"in": [], "out": []}
                        self.master_stores2rank[store][opposite].append(rank)

        else:
            for direction, stores in inout_stores.items():
                for store in stores:
                    assert isinstance(store, StoreMPI)
                    if direction == "in":
                        self.worker_in[store.name] = store
                    elif direction == "out":
                        self.worker_out[store.name] = store
                    else:
                        raise ValueError("Direction not understood: ",direction)

            neighboor={self.rank:{"in":[],"out":[]}}
            for k,store in self.worker_in.items():
                neighboor[self.rank]["in"].append(store.name)
            for k, store in self.worker_out.items():
                neighboor[self.rank]["out"].append(store.name)

            self.comm.send(obj=neighboor, dest=0)

    def fair_distribution(self, consumer_items: List[int], items: List) -> Dict[int, List]:
        """
        Fairly distribute items across consumer ranks.
        :param consumer_items: list of consumer ranks (e.g., [1, 2, 3])
        :param items: list of items to distribute (e.g.,  ["a", "b", "c", "d", "e"])
        :return: dict rank -> list of items (e.g. {
              1: ['a', 'd'],
              2: ['b', 'e'],
              3: ['c']
            }
        )
        """
        distribution = {rank: [] for rank in consumer_items}
        n = len(consumer_items)

        for i, item in enumerate(items): #TODO: complexity is improvable
            rank = consumer_items[i % n]
            distribution[rank].append(item)

        return distribution

    def _synch_items(self):
        if self.rank == 0:
            # Rank 0 collects items from all ranks
            gathered_items: Dict[str, List] = {}
            for i in range(1, self.size):
                out_stores = self.comm.recv(source=i)
                for store_name, items in out_stores.items():
                    if store_name not in gathered_items:
                        gathered_items[store_name] = []
                    gathered_items[store_name].extend(items)

            # Distribute items fairly
            ranks_message=[{} for _ in range(0, self.size)] # rank -> store -> message
            for i in range(len(ranks_message)):
                ranks_message[i]={}
                for store_name in gathered_items.keys():
                    ranks_message[i][store_name]=[]

            # E.g., {'buffer': ['item', 'item', 'item', 'item', 'item', 'item', 'item', 'item'], 'consumed': []}
            for store_name, items in gathered_items.items():
                consumer_ranks = self.master_stores2rank[store_name]["out"]
                if not consumer_ranks:
                    continue  # no consumers (e.g, sink store)

                # Recalculate fair share based on available items
                fair_shared_items = self.fair_distribution(consumer_ranks, items)
                for rank, items in fair_shared_items.items():
                    ranks_message[rank][store_name].extend(items)

            # e.g. [{}, {}, ['item', 'item', 'item', 'item', 'item', 'item', 'item', 'item']]
            for rank in range(1, self.size):
                msg = ranks_message[rank]
                self.comm.send(msg, dest=rank)
        else:
            # Worker: send out items
            out_data = {}
            for name, store in self.worker_out.items():
                items = []
                while store.items:
                    items.append(store.get())

                out_data[name] = items
            self.comm.send(out_data, dest=0)

            # Receive new input items
            in_data = self.comm.recv(source=0)
            for name, store in self.worker_in.items():
                incoming_items = in_data[name]
                for item in incoming_items:
                    store.put(item)

    def run(self, until: float, delta: float):

        self._synch_items()

        clock = 0.0
        while clock < until:
            clock = min(clock + delta, until)
            if self.local_env:
                self.local_env.run(until=clock)
            self._synch_items()
        self._synch_items()