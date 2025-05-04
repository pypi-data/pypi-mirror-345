from .future import Future
from .mailbox import Mailbox
from .message import Message
from diapyr.util import invokeall
from functools import partial
from queue import Queue

class Spawn:

    def __init__(self, executor):
        'Spawned actors will use threads from the given executor.'
        self.executor = executor

    def __call__(self, *objs):
        '''Create an actor backed by the given worker object(s), each of which is used in a single-threaded way.
        Calling a method on the returned actor returns a `Future` immediately, which eventually becomes done with the result of a worker method of the same name (or never if the worker method hangs).
        A worker method may be async, in which case it can await futures returned by other actors, releasing the worker in the meantime.'''
        def post(name, *args, **kwargs):
            future = Future()
            mailbox.add(Message(name, args, kwargs, future))
            return future
        def __getattr__(self, name):
            return partial(post, name)
        mailbox = Mailbox(self.executor, objs)
        return type(f"{''.join({type(obj).__name__: None for obj in objs})}Actor", (), {f.__name__: f for f in [__getattr__]})()

class Join:
    '''Make multiple futures awaitable as a unit. In the zero futures case this resolves (to an empty list) without suspending execution.
    Otherwise if any future hangs, so does this. Otherwise if any future failed, all such exceptions are raised as a chain. Otherwise all results are returned as a list.'''

    def __init__(self, futures):
        self.futures = futures

    def __await__(self):
        partials = []
        for f in self.futures:
            partials.append((yield f).result)
        return invokeall(partials)

class ManualExecutor:
    'Utilise the main (or any other) thread directly.'

    def __init__(self):
        self.q = Queue()

    def run(self):
        'Execute tasks until interrupted. Typical usage is for the main thread to call this after setting up the system.'
        while (task := self.q.get()) is not None:
            task()

    def submit(self, task, *args, **kwargs):
        self.q.put(partial(task, *args, **kwargs))

    def putinterrupt(self):
        'Cause exactly one thread to exit the `run` method soon.'
        self.q.put(None)
