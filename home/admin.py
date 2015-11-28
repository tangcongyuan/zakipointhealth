from django.contrib import admin
from django.contrib.admin.sites import NotRegistered


from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site

import logging
logger = logging.getLogger('zakipoint')

from session import *
from models import *

def unregister(cls):
    try:
        admin.site.unregister(cls)
    except NotRegistered:
        pass

unregister(User)
unregister(Group)
unregister(Company)
#unregister(Capability)
#unregister(UserRole)
#admin.site.register(Company)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Company)
