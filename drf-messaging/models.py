from django.db import models
from django.db.models import Q, Count, Max, F, Case, When, CharField, Value, OuterRef, Subquery
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone


# Create your models here.
class MessagesManager(models.Manager):
    def search_message(self, query):
        search_query = SearchQuery(query)
        search_vector = SearchVector('message')
        return self.get_queryset().annotate(rank=SearchRank(search_vector, search_query)) \
            .filter(rank__gte=0.1).order_by('-rank')

    def send_message(self, **kwargs):
        if (kwargs.get('sender_id') or kwargs.get('sender')) and (kwargs.get('receiver_id') or kwargs.get('receiver')):
            try:
                sender = kwargs.get('sender') or User.objects.get(id=kwargs['sender_id'])
                receiver = kwargs.get('receiver') or User.objects.get(id=kwargs['receiver_id'])
                message = kwargs.get('message')
            except User.DoesNotExist:
                raise ValueError("User does not exist", 400)
            except Exception:
                raise ValueError("Request error", 400)
            else:
                if not message:
                    raise ValueError("Message field is empty", 400)
                if sender == receiver:
                    raise ValueError("You can't send message to yourself", 400)

            message = self.create(sender=sender, receiver=receiver, message=message)
            return message
        else:
            return False

    def get_inbox(self, user, **kwargs):
        messages = self.get_queryset().filter(receiver=user)
        return messages

    def get_outbox(self, user, **kwargs):
        messages = self.get_queryset().filter(sender=user)
        return messages

    def read_message(self, mes_id):
        """
        Get message and set as read
        :param mes_id:
        :return:
        """
        message = self.get_queryset().get(id=mes_id)
        if not message.read:
            message.read_datetime = timezone.now()
        message.save()
        return message

    def get_chats(self, user):
        # Must be rewrite. Order_by doesn't work
        qs = self.get_queryset().filter(Q(receiver=user) | Q(sender=user)).annotate(
            user=Case(
                When(receiver=user, then=F('sender')),
                When(sender=user, then=F('receiver')),
                output_field=CharField(),
            ),
        ).values('user').annotate(
            unread_messages=Count(
                'pk',
                filter=Q(receiver=user, read=False),
            ),
            last_message_id=Max('pk')
        ).order_by('-last_message_id')

        return qs


    def get_chat(self, sender_id, receiver_id):
        """
        Mark as read and return chat messages
        :param sender_id:
        :param receiver_id:
        :return: queryset
        """
        self.set_read(sender_id, receiver_id)
        return self.get_queryset().filter(Q(sender_id=sender_id, receiver_id=receiver_id) |
                                              Q(sender_id=receiver_id, receiver_id=sender_id))

    def set_read(self, receiver_id, sender_id):
        """
        set all messages in chat as read
        :param sender_id:
        :param receiver_id:
        :return: messages count
        """
        return self.get_queryset().filter(sender_id=sender_id, receiver_id=receiver_id, read=False)\
            .update(read_datetime=timezone.now(), read=True)


class Messages(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['receiver']),
        ]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    sender = models.ForeignKey(
        User,
        related_name='user_sender',
        on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        User,
        related_name='user_receiver',
        on_delete=models.CASCADE
    )

    message = models.TextField()

    datetime = models.DateTimeField(
        auto_now=True
    )

    read = models.BooleanField(
        default=False
    )

    read_datetime = models.DateTimeField(
        null=True,
        default=None,
        blank=True
    )

    objects = MessagesManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.read_datetime:
            self.read = True
        else:
            self.read = False
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "%s %s (%s) to %s %s (%s): %s" % (self.sender.first_name, self.sender.last_name,
                                                 self.sender.profile.phone_number or self.sender.email,
                                                 self.receiver.first_name, self.receiver.last_name,
                                                 self.receiver.profile.phone_number or self.receiver.email,
                                                 self.message[:20])
