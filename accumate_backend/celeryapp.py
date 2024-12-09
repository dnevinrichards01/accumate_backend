import os
from celery import Celery
from kombu import Queue
import kombu
from .settings import REDIS_URL, BASE_DIR
import ssl
import logging




"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "accumate_backend.settings")
app = Celery("accumate_backend",
            broker=REDIS_URL,
            broker_transport_options = {
                'ssl': {
                    'ssl_ca_certs': "/Users/nevinrichards/Downloads/accumate/accumate_backend/redis.pem", 
                    'ssl_cert_reqs': ssl.CERT_REQUIRED
                }
            }
            )
"""
# Create a strict SSL context
ssl_context = ssl.create_default_context(cafile=os.path.join(BASE_DIR,"redis.pem"))
ssl_context.check_hostname = True  # Verify the server hostname
ssl_context.verify_mode = ssl.CERT_REQUIRED  # Enforce certificate verification



# Celery Configuration
app = Celery(
    "accumate_backend",
    broker=REDIS_URL,
    broker_transport_options={
        "ssl": ssl_context
    }
)

app.autodiscover_tasks()
app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL
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