# REF: https://docs.djangoproject.com/en/1.6/topics/auth/default/
from django.db import models

# Create your models here.
from django.contrib.auth.models import User, Group, Permission
from zphalfa import json_field
import logging
logger = logging.getLogger('zakipoint')

