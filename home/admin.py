from django.contrib import admin
from django.contrib.admin.sites import NotRegistered


from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site

import logging, sys
logger = logging.getLogger('zakipoint')

from session import *
from models import *

def unregister(cls):
    try:
        admin.site.unregister(cls)
        #logger.info('Admin unregistered %s', cls.__name__)
    except NotRegistered:
        logger.info('Admin could not unregister %s', cls.__name__)

def register(cls):
    try:
        admin.site.register(cls)
        #logger.info('Admin registered %s', cls.__name__)
    except NotRegistered:
        logger.info('Admin could not register %s', cls.__name__)

unregister(User)
unregister(Group)
unregister(Company)
#unregister(Capability)
#unregister(UserRole)
#admin.site.register(Company)
register(User)
register(Group)
register(Company)
