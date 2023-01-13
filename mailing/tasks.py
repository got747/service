import os
import requests
from django.utils import timezone
from celery.utils.log import get_task_logger

from .models import Message, Client, Mailing
from service_notification.celery import app

logger = get_task_logger(__name__)

URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")


@app.task(bind=True, retry_backoff=True)
def send_message(self, message_id, client_id, mailing_id, url=URL, token=TOKEN):
    mail = Mailing.objects.get(pk=mailing_id)
    client = Client.objects.get(pk=client_id)

    if mail and client:
        if mail.to_send:

            data = {"id": message_id, "phone": client.phone_number, "text": mail.text}

            header = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            try:
                # requests.post(url=url + str(data["id"]), headers=header, json=data)
                pass
            except requests.exceptions.RequestException as exc:
                logger.error(f"Message if: {data['id']} is error")
                raise self.retry(exc=exc)
            else:
                logger.info(f"Message id: {data['id']}, Sending status: 'Sent'")
                Message.objects.filter(pk=data["id"]).update(
                    status=Message.ChoicesStatuses.SENT
                )
            Message.objects.filter(pk=data["id"]).update(
                status=Message.ChoicesStatuses.SENT
            )
        else:

            logger.info(
                f"The mailing time has been changed, the task has been moved to ${mail.date_start}"
            )
            return self.retry(eta=mail.date_start, expires=mail.date_end)

    else:
        logger.info("Mailing list or client has been deleted")
