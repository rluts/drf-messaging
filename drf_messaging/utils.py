from rest_framework import serializers
from collections import OrderedDict
from .models import Attachment

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ExtRelatedField(serializers.RelatedField):
    """
    Temporary fixing DRF bug. Please update DRF after bug fix
    https://github.com/encode/django-rest-framework/issues/5141
    """
    def to_representation(self, obj):
        logger.debug("to rep: " + str(obj))
        return {
            'id': obj.pk,
        }

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                item.pk,
                self.display_value(item)
            )
            for item in queryset
        ])

    def to_internal_value(self, data):
        try:
            queryset = self.get_
        except:
            raise ValueError("Unknown request", 400)


def get_user_info_from_instance(instance):
    info = {
        "id": instance.id,
        "name": "{} {}".format(instance.first_name, instance.last_name),
        "email": instance.email
    }
    return info
