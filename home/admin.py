from django.contrib import admin
from django.contrib.admin.sites import NotRegistered


from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site

import logging
logger = logging.getLogger('zakipoint')

from session import *
from models import *

try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User)

try:
    admin.site.unregister(Group)
except:
    pass
admin.site.register(Group)

try:
    admin.site.unregister(Company)
except NotRegistered:
    pass
admin.site.register(Company)
admin.site.register(Capability)
admin.site.register(UserRole)
