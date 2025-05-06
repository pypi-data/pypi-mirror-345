import multiprocessing
from typing import *
import os
import pickle
import sys

from SerializableSimpy.core import Environment

class MPGlobalEnv:
    def __init__(self, initial_time: float = 0.0):
        self.initial_time = initial_time
        self.envs: List[Environment] = []  # store all registered environments
        self.processes: List[multiprocessing.Process] = []
        self._manager = multiprocessing.Manager()
        self._now = multiprocessing.Value('d', initial_time)  # global time shared between processes
        self._now_lock = multiprocessing.Lock()

    def env(self, env: Environment):
        """Register a local environment."""
        self.envs.append(env)

    def _run_local_env(self, env: Environment, until: float, delta: float, barrier: multiprocessing.Barrier):
        """Target function for each process."""
        env._initialize()
        barrier.wait()
        clock = 0.0
        while clock < until:
            clock = min(clock + delta, until)
            env.run(until=clock)
            barrier.wait()
        barrier.wait()

    def set_now(self, now: float):
        with self._now_lock:
            self._now.value = now

    def get_now(self) -> float:
        with self._now_lock:
            return self._now.value

    def run(self, until: float, delta: float):
        """Run the global simulation until the given time, synchronizing every `delta`."""
        num_processes = len(self.envs)
        barrier = multiprocessing.Barrier(num_processes)

        self.processes.clear()

        for env in self.envs:
            p = multiprocessing.Process(target=self._run_local_env, args=(env, until, delta, barrier))
            p.start()
            self.processes.append(p)

        for p in self.processes:
            p.join()

