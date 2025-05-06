import multiprocessing
from typing import Optional, Any

class StoreMP:
    def __init__(self, capacity=float('inf')):
        self._capacity = capacity
        self.items=multiprocessing.Manager().list()
        self.lock=multiprocessing.Manager().Lock()


    def put(self, obj:Any):
        if obj:
            with self.lock:  # ask the lock
                if len(self.items) < self._capacity:
                    self.items.append(obj)

    def get(self) -> Optional[Any]:
        obj=None
        with self.lock: # ask the lock
            if len(self.items)>0:
                obj=self.items.pop()
        return obj
