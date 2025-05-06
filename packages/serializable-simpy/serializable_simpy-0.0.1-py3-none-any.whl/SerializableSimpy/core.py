from heapq import heappop, heappush
from collections import deque
from typing import *
from functools import partial, wraps
import os

class EventInQueue: # the events can be sorted by the queue
    def __init__(self, time, func_ptr, func_args):
        self.time = time
        self.func_ptr = func_ptr
        self.func_args = func_args

    def __lt__(self, other):
        return self.time < other.time

def _extract_names(event_callable: Callable) -> str:
    """
    This function allows to extract event names: either class name (coarse grain), or object name (fine grain).
    This is usefull for retro-engineering activity
    @param event_callable: the next event pop
    @return: class name, object name
    """
    instance = getattr(event_callable, "__self__", None)
    class_name = instance.__class__.__name__
    method_name=event_callable.__name__
    object_name = getattr(instance, "name", "Attribute not found") if instance else "None"

    class_point_method=class_name+"."+method_name
    return class_name, class_point_method, object_name

def trace(env, callback):
    """Replace the ``step()`` method of *env* with a tracing function
    that calls *callbacks* with an events time, priority, ID and its
    instance just before it is processed.
    Simpy doc: https://simpy.readthedocs.io/en/latest/topical_guides/monitoring.html
    """
    def get_wrapper(env_step, callback):
        """Generate the wrapper for env.step()."""
        @wraps(env_step)
        def tracing_step():
            """Call *callback* for the next event if one exist before
            calling ``env.step()``."""
            if len(env.queue):
                t, prio, eid, event = env._queue[0]
                callback(t, prio, eid, event)
            return env_step()
        return tracing_step

    env.step = get_wrapper(env.step, callback)

class Environment:
    def __init__(self, initial_time:float=0):
        self.queue:List[EventInQueue] = [] # <-- heap
        self.now:float = initial_time
        self.processes:List["Process"] = []
        self._init=False
        self._num_insert=0
        self._num_pop=0
        self._until=0.

    def process(self, p):
        #if isinstance(p, Process): # TODO <-- to remove and replaced by Process2
        #    self.lps.append(p)
        #elif isinstance(p, Store):
        self.processes.append(p)


        self._init=False
    def _initialize(self):
        for p in self.processes:
            p.on_initialize(env=self)
        self._init = True

    def get_now(self)->float:
        """
        Common getter with EnvironmentMP, in envionmentMP getting this value is protected with mutex.
        :return:
        """
        return self.now

    def set_now(self, now: float):
        self.now=now

    def run(self, until:float):
        if not self._init:
            self._initialize()

        func_ptr="do_nothing"
        self._until = until

        while until > self.get_now():
            now, func_ptr, func_args=self.next_event(until)
            if until > now:
                # run it
                self.set_now(now)
                func_ptr(*func_args)
            else:
                # reschedule for future
                # Strategy 1: ex. simpn project, where we compute the event even if it is after "until"
                # event = EventInQueue(self.get_now(), func_ptr, func_args)
                # heappush(self.queue, event)
                # Strategy 2: ex. simpy project, where the event is re-scheduled
                if func_ptr != "do_nothing":
                    event = EventInQueue(now, func_ptr, func_args)
                    heappush(self.queue, event) # reschedule for a future Environment.run(until2) with until2 > current until
                self.set_now(until)  # exit

    def timeout(self, t, func_ptr, func_args):
        event=EventInQueue(self.get_now() + t, func_ptr, func_args)
        heappush(self.queue, event)
        self._num_insert+=1

    def next_event(self, until)->Tuple[float, Callable, Tuple[object]]:
        if not self.queue:
            #print(f"t:{until} STOP_EVENT pid:{os.getpid()}")
            return until, "do_nothing", tuple()
        event=heappop(self.queue)
        #print(event)
        self._num_pop+=1
        return event.time, event.func_ptr, event.func_args

class Process: # ABSTRACT CLASS
    def on_initialize(self, env:Environment):
        pass

class Store:
    def __init__(self, capacity=float('inf')):
        self.env = None
        self._capacity = capacity
        self.items=[]
        self.waiting=[]
    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def on_put(self, obj):
        if len(self.items) < self._capacity:
            self.items.append(obj)
            if self.waiting:
                while (self.waiting and self.items):
                    #self.env.timeout(10, self.waiting.pop(), tuple([self.items.pop()]))
                    self.waiting.pop()(self.items.pop())

    def on_get(self, pro):
        if self.items:
            pro(self.items.pop())
        else:
            self.waiting.append(pro)

# URL: https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/events.py?ref_type=heads#L51
class Event:
    def __init__(self, env: Environment):
        self.env = env
        self.callbacks = []
        self.triggered = False

    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def add_callback(self, callback:Callable, args=tuple()):
        if self.triggered:
            callback(*args)
        else:
            self.callbacks.append((callback, args))

    def on_trigger(self):
        self.triggered = True
        while self.callbacks:
            callback, args = self.callbacks.pop()
            callback(*args)

class Resource:
    def __init__(self, env: Environment, capacity: int = 1):
        self.env = env
        self.capacity = capacity
        self.users = 0
        self.queue = deque()

    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def on_request(self, what_to_do_when_release: Callable, args:tuple = tuple()):
        if self.capacity > self.users:
            self.users += 1
            #self.users.append((what_to_do_when_release,args))
            what_to_do_when_release(*args)
        else:
            self.queue.append((what_to_do_when_release,args))


    def on_release(self, what_to_do_when_release: Callable, args:tuple = tuple()):
        self.users -= 1

        # Some objects in queues are transfered in users
        while self.queue and self.users<self.capacity:
            self.users += 1
            call, args = self.queue.pop()
            call(*args)
