from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver

from .models import Mailing, Client, Message
from .tasks import send_message

@receiver(post_save, sender=Mailing, dispatch_uid="builder_task_on_mailing")
def builder_tasks_on_mailing(sender, instance, created, **kwargs):
    if created:
        mailing = Mailing.objects.get(pk=instance.id)

        clients = Client.objects.filter(
            Q(tag=mailing.tag) | Q(operator_code=mailing.operator_code)
        )

        for client in clients:
            Message.objects.create(
                status = Message.ChoicesStatuses.NO_SENT,
                client_id = client.id,
                mailing_id = mailing.id
            )

            message = Message.objects.get(mailing_id=mailing.id, client_id=client.id)

            if mailing.to_send:
                send_message.apply_async((message.id, client.id, mailing.id),
                                         expires=mailing.mailling_end_at)
            else:
                send_message.apply_async((message.id, client.id, mailing.id),
                                         eta=mailing.mailling_start_at, expires=mailing.mailling_end_at)
