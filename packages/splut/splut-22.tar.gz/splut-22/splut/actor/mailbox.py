from threading import Lock

class Worker:

    def __init__(self, obj):
        self.idle = True
        self.obj = obj

class Mailbox:

    def __init__(self, executor, objs):
        self.queue = []
        self.lock = Lock()
        self.executor = executor
        self.workers = [Worker(obj) for obj in objs]

    def add(self, message):
        with self.lock:
            for worker in self.workers:
                if worker.idle:
                    task = message.taskornone(worker.obj, self)
                    if task is not None:
                        self.executor.submit(self._run, worker, task)
                        worker.idle = False
                        return
            if message.anyhit(worker.obj for worker in self.workers if not worker.idle):
                self.queue.append(message)
                return
        message.setmiss()

    def _another(self, worker):
        with self.lock:
            for i, message in enumerate(self.queue):
                task = message.taskornone(worker.obj, self)
                if task is not None:
                    self.queue.pop(i)
                    return task
            worker.idle = True

    def _run(self, worker, task):
        while True:
            task()
            task = self._another(worker)
            if task is None:
                break
