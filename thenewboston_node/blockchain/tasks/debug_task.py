# TODO(dmu) HIGH: Remove this example task once real tasks are created
from celery import shared_task


@shared_task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
