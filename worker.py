
import logging
import redis

from rq import Connection, Queue, Worker

logging.basicConfig(filename='worker.log', level=logging.INFO)


connection = redis.from_url('redis://localhost:6379/0')

with Connection(connection):
    worker = Worker(list(map(Queue, ['default'])))
    x = worker.work()


