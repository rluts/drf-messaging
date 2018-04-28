import re
from .models import BlackList
from django.core.exceptions import ValidationError


def blacklist_validator(value):
    blacklists = BlackList.objects.all()
    if not value:
        raise ValidationError('message is required field')
    for blacklist in blacklists:
        if (blacklist.regex and re.search(blacklist.word, value)) or \
                        not blacklist.regex and blacklist.word in value:
            raise ValidationError("Blacklist error")
