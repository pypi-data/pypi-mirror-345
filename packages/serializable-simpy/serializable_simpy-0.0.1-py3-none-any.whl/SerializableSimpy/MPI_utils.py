from mpi4py import MPI
from typing import *

from typing import Optional, Any

class StoreMPI:
    def __init__(self,name:str, capacity=float('inf')):
        """
        :param name: a name is mandatory with MPI implementation. The name allows the manager (rank=0) to know the direction of items (from X to Y).
        :param capacity: maximum capacity of the Store object. Overflowing the item capacity and the item is lost (without any error).
        """
        self._capacity = capacity
        self.items=[]
        self.name=name

    def put(self, obj:Any):
        if len(self.items) < self._capacity:
            self.items.append(obj)

    def get(self) -> Optional[Any]:
        obj=None
        if len(self.items)>0:
            obj=self.items.pop()
        return obj

def _synchronize_stores_waiting(comm, local_store, rank_store_coordinator: int):
    rank = comm.Get_rank()

    all_items = comm.gather(local_store.waiting, root=rank_store_coordinator)
    if rank == rank_store_coordinator:
        all_items = [item for sublist in all_items for item in sublist]
    local_store.waiting = comm.bcast(all_items, root=rank_store_coordinator)


def _synchronize_stores_items(comm, local_store, rank_store_coordinator: int):
    rank = comm.Get_rank()

    all_items = comm.gather(local_store.items, root=rank_store_coordinator)
    if rank == rank_store_coordinator:
        all_items = [item for sublist in all_items for item in sublist]
    local_store.items = comm.bcast(all_items, root=rank_store_coordinator)


def _broadcast_stores_waiting(comm, local_store, rank_store_coordinator: int):
    local_store.waiting = comm.bcast(local_store.waiting, root=rank_store_coordinator)


def _broadcast_stores_items(comm, local_store, rank_store_coordinator: int):
    local_store.items = comm.bcast(local_store.items, root=rank_store_coordinator)


def _intersection_stores_waiting(comm, local_store, rank_store_coordinator):
    rank = comm.Get_rank()

    all_waiting = comm.gather(local_store.waiting, root=rank_store_coordinator)
    if rank == rank_store_coordinator:
        # Compute the intersection of all waiting lists
        intersection_waiting = set(all_waiting[0])
        for waiting_list in all_waiting[1:]:
            intersection_waiting &= set(waiting_list)
        all_waiting = list(intersection_waiting)
    else:
        all_waiting = None

    local_store.waiting = comm.bcast(all_waiting, root=rank_store_coordinator)


def _intersection_stores_items(comm, local_store, rank_store_coordinator):
    rank = comm.Get_rank()

    all_items = comm.gather(local_store.items, root=rank_store_coordinator)
    if rank == rank_store_coordinator:
        # Compute the intersection of all items lists
        intersection_items = set(all_items[0])
        for items_list in all_items[1:]:
            intersection_items &= set(items_list)
        all_items = list(intersection_items)
    else:
        all_items = None

    local_store.items = comm.bcast(all_items, root=rank_store_coordinator)


def _scattering_stores_items(comm, local_store, rank_store_coordinator: int):
    rank = comm.Get_rank()

    if rank == rank_store_coordinator:
        all_items = local_store.items
        scatter_data = [all_items[i::comm.Get_size()] for i in range(comm.Get_size())]
    else:
        scatter_data = None

    local_store.items = comm.scatter(scatter_data, root=rank_store_coordinator)


def _scattering_stores_waiting(comm, local_store, rank_store_coordinator: int):
    rank = comm.Get_rank()

    if rank == rank_store_coordinator:
        all_waiting = local_store.waiting
        scatter_data = [all_waiting[i::comm.Get_size()] for i in range(comm.Get_size())]
    else:
        scatter_data = None

    local_store.waiting = comm.scatter(scatter_data, root=rank_store_coordinator)


def aggregate_stores(comm, local_store, rank_store_coordinator: int, ranks: Optional[List[int]] = None):
    if ranks is None:
        # All
        _synchronize_stores_items(comm, local_store, rank_store_coordinator)
        _synchronize_stores_waiting(comm, local_store, rank_store_coordinator)
    else:

        # Sub group (E.g., only consumers or only producers)
        sub_group = MPI.COMM_WORLD.group.Incl(ranks)
        sub_comm = comm.Create_group(sub_group)

        if sub_comm != MPI.COMM_NULL:
            _synchronize_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
            _synchronize_stores_waiting(sub_comm, local_store, ranks.index(rank_store_coordinator))
        sub_comm.Free()


def broadcast_stores(comm, local_store, rank_store_coordinator: int, ranks: Optional[List[int]] = None):
    if ranks is None:
        # All
        _broadcast_stores_items(comm, local_store, rank_store_coordinator)
        _broadcast_stores_waiting(comm, local_store, rank_store_coordinator)
    else:

        # Sub group (E.g., only consumers or only producers)
        sub_group = MPI.COMM_WORLD.group.Incl(ranks)
        sub_comm = comm.Create_group(sub_group)

        if sub_comm != MPI.COMM_NULL:
            _broadcast_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
            _broadcast_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
        sub_comm.Free()


def intersection_stores(comm, local_store, rank_store_coordinator: int, ranks: Optional[List[int]] = None):
    if ranks is None:
        # All
        _intersection_stores_items(comm, local_store, rank_store_coordinator)
        _intersection_stores_waiting(comm, local_store, rank_store_coordinator)
    else:

        # Sub group (E.g., only consumers or only producers)
        sub_group = MPI.COMM_WORLD.group.Incl(ranks)
        sub_comm = comm.Create_group(sub_group)

        if sub_comm != MPI.COMM_NULL:
            _intersection_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
            _intersection_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
        sub_comm.Free()


def scattering_stores(comm, local_store, rank_store_coordinator: int, ranks: Optional[List[int]] = None):
    if ranks is None:
        # All
        _scattering_stores_items(comm, local_store, rank_store_coordinator)
        _scattering_stores_waiting(comm, local_store, rank_store_coordinator)
    else:

        # Sub group (E.g., only consumers or only producers)
        sub_group = MPI.COMM_WORLD.group.Incl(ranks)
        sub_comm = comm.Create_group(sub_group)

        if sub_comm != MPI.COMM_NULL:
            _scattering_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
            _scattering_stores_items(sub_comm, local_store, ranks.index(rank_store_coordinator))
        sub_comm.Free()
