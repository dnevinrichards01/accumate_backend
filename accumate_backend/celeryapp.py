import os
from celery import Celery
from kombu import Queue
import kombu
from .settings import REDIS_URL, BASE_DIR
import ssl
import logging

REDIS_URL = REDIS_URL.split('?')[0] + '?ssl_cert_reqs=CERT_NONE'

# Celery Configuration
app = Celery("accumate_backend")
app.autodiscover_tasks()
app.conf.broker_url = REDIS_URL
app.conf.broker_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE} # doesn't work
app.conf.result_backend = REDIS_URL
app.conf.result_backend_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE} # doesn't work
app.conf.broker_connection_retry_on_startup = True
app.conf.accept_content = ["application/json"]
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.task_default_queue = "main"
app.conf.task_create_missing_queues = True
app.conf.task_queues = (Queue("main"),)
app.conf.broker_pool_limit = 1
app.conf.broker_connection_timeout = 30
app.conf.worker_prefetch_multiplier = 1
app.conf.redbeat_redis_url = REDIS_URL