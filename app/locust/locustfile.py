"""
API's load testing with locust.
"""
from datetime import datetime

from locust import (
    HttpUser,
    task
)


class QuickstartUser(HttpUser):

    def on_start(self):
        res = self.client.post('user/api/v1/token/login/', data={
            "email": "admin@example.com",
            "password": "123"
        }).json()
        self.client.headers = {
            "Authorization": f"Token {res.get('token', None)}"
            }

    @task
    def task_get_post_list(self):
        self.client.get('blog/api/v1/posts/')

    @task
    def task_post_sample_post(self):
        self.client.post('blog/api/v1/posts/', data={
            'title': 'Sample title',
            'content': 'Sample content',
            'status': True,
            'published_date': datetime.now()
        })
