"""
Celery configurations.
"""
import os
from celery import Celery

from django.conf import settings

from kombu import Queue, Exchange
from mail_templated import EmailMessage


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object(settings, namespace='CELERY')

app.conf.task_queues = [
    Queue('tasks', Exchange('tasks'), routing_key='tasks',
          queue_arguments={'x-max priority': 10})
]

app.conf.task_acks_late = True
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_concurrency = 1


@app.task(queue='tasks')
def send_email_activation_account(email=None, context=None):
    email_object = EmailMessage(
        'email/activation.tpl',
        {'context': context}, 'DjangoAdmin@example.com',
        to=[email]
    )
    email_object.send()

    return 'Done'


@app.task(queue='tasks')
def send_email_reset_password(email=None, token=None, link=None):
    email_object = EmailMessage(
        'email/reset-password.tpl',
        {'token': token, 'link': link}, 'DjangoAdmin@example.com',
        to=[email]
    )
    email_object.send()

    return 'Done'


app.autodiscover_tasks()
