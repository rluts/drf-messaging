# drf-messaging
Simple async and sync messaging app for Django Rest Framework (Django 2 only)

Features:
+ Facebook-style chat API
+ Websocket-based chat
+ Words blacklist
+ Files attachments

### Installation:
* Install redis-server
* Install requirements.txt
* Configure location /socket/ on your proxy settings
* Configure your Django settings:
  * Rest framework

```python
# REST
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'drf_messaging.exceptions.api_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}
```
  * ASGI and Channels
```python
# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}
ASGI_APPLICATION = "drf_messaging.routing.application"
```
  * Add drf_messaging to your installed apps
 ```python
INSTALLED_APPS = [
	...
    'channels',
    'rest_framework',
    'rest_framework.authtoken',

	...
	
    'drf_messaging.apps.DRFMessagingConfig'
]
```
