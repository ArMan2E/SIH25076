from celery import Celery
import os

broker = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend = os.environ.get('CELERY_RESULT_BACKEND', broker)
celery = Celery('krishi_worker', broker=broker, backend=backend)
celery.conf.task_routes = {
    'worker.tasks.process_incoming_call': {'queue': 'calls'}
}
