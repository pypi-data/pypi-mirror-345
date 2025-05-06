import unittest

from SerializableSimpy.core import Environment, Process, Store, Event, Resource


class MyTestCase(unittest.TestCase):

    def test_process(self):
        out = set([])

        class Clock(Process):
            def on_initialize(self, env):
                self.env = env
                self.on_yield()

            def on_yield(self):
                out.add("It is " + str(int(self.env.get_now())))
                self.env.timeout(1, self.on_yield, ())  # `tuple()` means no argument for `on_yield()`

        env = Environment()
        env.process(Clock())
        env.run(until=3)

        expected_set = set(["It is 0", "It is 1", "It is 2"])
        self.assertTrue(out == expected_set)

    def test_event(self):
        out = set([])

        class Machine(Process):
            def __init__(self, name):
                self.name = name

            def on_initialize(self, env):
                self.env = env
                self.state = "IDLE"
                self.on_yield()

            def on_yield(self):
                out.add(f"{self.name} time: {int(self.env.get_now())} state: {self.state}")
                self.env.timeout(1, self.on_yield, tuple())  # `tuple()` means no argument for `on_yield()`

            def on_wake_up(self):
                self.state = "WORKING"

        env = Environment()
        alarm = Event(env)
        env.process(alarm)

        for i in range(3):
            m = Machine("m" + str(i))
            alarm.add_callback(m.on_wake_up)
            env.process(m)

        env.run(until=2)
        alarm.on_trigger()
        env.run(until=4)

        s = set([])
        s.add("m0 time: 0 state: IDLE")
        s.add("m1 time: 0 state: IDLE")
        s.add("m2 time: 0 state: IDLE")
        s.add("m0 time: 1 state: IDLE")
        s.add("m1 time: 1 state: IDLE")
        s.add("m2 time: 1 state: IDLE")
        s.add("m1 time: 2 state: WORKING")
        s.add("m2 time: 2 state: WORKING")
        s.add("m0 time: 2 state: WORKING")
        s.add("m1 time: 3 state: WORKING")
        s.add("m2 time: 3 state: WORKING")
        s.add("m0 time: 3 state: WORKING")

        self.assertTrue(s == out)

    def test_resource(self):
        out = set([])

        class MyProcess(Process):
            def __init__(self, env: Environment, resource: Resource):
                self.env = env
                self.resource = resource

            def on_initialize(self, env: Environment):
                self.env = env
                self.run()

            def run(self):
                out.add(f"Process started at time {self.env.get_now()}. Request resource")
                self.resource.on_request(self.use_resource)

            def use_resource(self):
                out.add(f"Resource acquired at time {self.env.get_now()}. Released in 5min.")
                self.env.timeout(5, self.resource.on_release, tuple([self.use_resource,()]))

        env = Environment()
        r = Resource(env, capacity=2)
        env.process(r)

        for i in range(5):
            p = MyProcess(env, r)
            env.process(p)

        env.run(until=20)

        s = set([])
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 0. Released in 5min.")
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 0. Released in 5min.")
        s.add("Process started at time 0. Request resource")
        s.add("Process started at time 0. Request resource")
        s.add("Process started at time 0. Request resource")
        s.add("Resource acquired at time 5. Released in 5min.")
        s.add("Resource acquired at time 5. Released in 5min.")
        s.add("Resource acquired at time 10. Released in 5min.")

        self.assertTrue(s == out)

    def test_store(self):
        #s=set([])
        class Producer:
            def __init__(self, store: Store, cycle_time: float):
                self.env = None
                self.store = store
                self.item_id = 0
                self.cycle_time = cycle_time

            def on_initialize(self, env):
                self.env = env
                self.env.timeout(self.cycle_time, self.on_yield, tuple())  # launch the producing loop

            def on_yield(self):
                self.store.on_put(f"item{self.item_id}")
                self.env.timeout(self.cycle_time, self.on_yield, tuple())  # loop on itself every 5
                self.item_id += 1

        class Consumer(Process):
            def __init__(self, store: Store, cycle_time: float):
                self.env = None
                self.store = store
                self.cycle_time = cycle_time

            def on_initialize(self, env):
                self.env = env
                self.store.on_get(self.on_yield)  # the consumer is immediately ready to receive a new item

            def on_yield(self, msg):
                #s.add(f'Consumer receives {msg} at {self.env.now}')
                # self.store.on_get(self.on_yield)
                self.env.timeout(self.cycle_time, self.store.on_get, tuple([self.on_yield]))

        env = Environment()
        store = Store(capacity=2)
        env.process(Producer(store, cycle_time=1))
        env.process(Consumer(store, cycle_time=2))  # consumer is slower
        env.run(until=10)


        self.assertTrue(len(store.items)==2)


if __name__ == "__main__":
    unittest.main()
